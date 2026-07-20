from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent, EmailContent
from messenger import send_email

import asyncio


class ResearchManager:

    async def run(self, query: str, recipient_email: str):
        """Run the deep research process"""

        trace_id = gen_trace_id()

        with trace("Research trace", trace_id=trace_id):

            yield f"Starting research. Trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"

            search_plan = await self.plan_searches(query)

            yield f"Searches planned, starting {len(search_plan.searches)} searches..."

            search_results = await self.perform_searches(search_plan)

            yield "Searches complete, writing report..."

            report = await self.write_report(query, search_results)

            yield "Generating email..."

            email_content = await self.generate_email(report)

            yield "Sending email..."

            try:
                await asyncio.to_thread(
                    send_email,
                    recipient=recipient_email,
                    subject=email_content.subject,
                    text_body=email_content.text_body,
                    html_body=email_content.html_body,
                )
                email_status = f"✅ Report emailed to {recipient_email}"
            except Exception as e:
                email_status = f"⚠️ Email could not be sent: {e}"

            yield f"**{email_status}**\n\n---\n\n{report.markdown_report}"

    async def plan_searches(self, query: str) -> WebSearchPlan:
        result = await Runner.run(
            planner_agent,
            f"Query: {query}"
        )
        return result.final_output

    async def perform_searches(
        self,
        search_plan: WebSearchPlan
    ) -> list[str]:

        tasks = [self.search(item) for item in search_plan.searches]

        return await asyncio.gather(*tasks)

    async def search(
        self,
        item: WebSearchItem
    ) -> str | None:

        input_message = (
            f"Search term: {item.query}\n"
            f"Reason for searching: {item.reason}"
        )

        result = await Runner.run(
            search_agent,
            input_message
        )

        return result.final_output

    async def write_report(
        self,
        query: str,
        search_results: list[str]
    ) -> ReportData:

        input_message = (
            f"Original query: {query}\n"
            f"Summarized search results: {search_results}"
        )

        result = await Runner.run(
            writer_agent,
            input_message
        )

        return result.final_output

    async def generate_email(
        self,
        report: ReportData
    ) -> EmailContent:

        result = await Runner.run(
            email_agent,
            report.markdown_report
        )

        return result.final_output