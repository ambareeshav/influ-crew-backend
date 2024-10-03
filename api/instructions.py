from composio_crewai import ComposioToolSet
from crewai import Agent, Task, Crew, Process
from composio_crewai import Action
from textwrap import dedent

def run(input):
    entity_id = "default"
    toolset = ComposioToolSet(entity_id=entity_id)
    tools = toolset.get_tools(actions=[Action.TAVILY_TAVILY_SEARCH])

    research_agent = Agent(
                role="Company researcher",
                goal="Obtaining information on given company/product",
                backstory="You are part of a Influencer Evaluation system and responsible of finding information on a company/product",
                verbose=False,
                tools=tools,
                llm = "groq/llama3-70b-8192"
            )

    comp_analysis_agent = Agent(
                role="Company analysis",
                goal="Obtaining the competitors of given company/product",
                backstory="You are part of a Influencer Evaluation system and responsible of performing competitor analysis on a company/product",
                verbose=False,
                tools=tools,
                llm = "groq/llama3-70b-8192"
            )

    instructions_agent = Agent(
                role="Instructions writer",
                goal="Writing instructions for openai assistant",
                backstory="You are part of a Influencer Evaluation system and responsible of writing instructions for openai assistant that will be used to evaluate youtube channels given video data",
                verbose=False,
                llm = "groq/llama3-70b-8192"
            )

    research_task = Task(
        description=dedent(f"""
            1. Perform a comprehensive and deep research about {input} and return all relevant infromation
            2. Make exactly one tool call
            3. These are the only inputs you must provide to the tool, nothing else
                        "query": 
                        "search_depth": 
                        "max_results": 
        """),
        agent=research_agent,
        expected_output="perform research and return data",
        verbose=False,
    )

    comp_analysis_task = Task(
        description=dedent(f"""
            1. Perform a competitor analysis of {input} and return all relevant infromation
            2. Return a numbered list of competitors of the input
            3. Make exactly one tool call
            4. These are the only inputs you must provide to the tool, nothing else
                        "query": 
                        "search_depth": 
                        "max_results": 
        """),
        agent=comp_analysis_agent,
        expected_output="A list of competitors with a short description",
        verbose=False,
    )

    instructuions_task = Task(
        description=dedent(f"""
            1. You will write instructions for an openai assitant to rank youtube channels relevancy on {input}
            2. The assitant will be given the youtube channel data, your instructions should help it analyze that data against the researched data to find out whether the channel is a right fit for {input}
            3. Use the below format loosely to write the instructions: 
                You are an assistant tasked with ranking influencers on certain criteria to promote our product, <INSERT RELEVANT INFORMATION HERE>.
                Your input data will be JSON of Videos details of a YouTube channel 
                1. Information about {input}:
                            a. Description - <INSERT RELEVANT INFORMATION HERE>
                            b. Features - <INSERT RELEVANT INFORMATION HERE>
                            c. Target Market - <INSERT RELEVANT INFORMATION HERE>
                            d. Competitors - <INSERT RELEVANT INFORMATION HERE>
                2. Ideal Customer Profiles (ICPs) - <INSERT RELEVANT INFORMATION HERE>
                3. Evaluation Criteria
                            a. Relevance 
                                Content Focus: <INSERT RELEVANT INFORMATION HERE>
                                Audience Alignment: <INSERT RELEVANT INFORMATION HERE>
                                Competitors: <INSERT RELEVANT INFORMATION HERE> Any mentin of competitors in video title, description. summary, transcipt should default the channels rank to irrelevant
                                Video Titles: The input video data will have a list of the channels recent video titles, analyze the titles to get a sense of what the user generally promotes and rank accordingly
                            b. Impact
                                Engagement Metrics: Assess the number of views, likes, comments, and overall engagement relative to the influencer's subscriber count. Ensure consistency in stats across videos. An influencer with a lot of subscribers and views need not necessarily have high impact. 
                                Content Depth: Analyze the transcript of every single video, judge the content depth based on the transcript evaluation and length of the video. The influencer should demonstrate thought leadership and provide in-depth, actionable content that resonates with their audience, particularly in paid advertising and performance marketing. Prioritize high engagement rates over follower counts. 
                                Frequency of videos: 2-4 videos in the last 30 days is a good frequency. Anything more is better but may also suggest lower depth, if the influencer has not posted videos for a long period of time (1 month or more), that indicates that the influencer may not be actively working on the channel and that should affect the frequency rating accordingly.
                                Promotions:An influencer selling a course, having a membership area or running a newsletter are ones who are looking to monetize their following and have greater influence. This means they are likely to be open to partnerships and sponsorships and could have higher impact.
                            c. Winnability
                                Approachability: Influencers with medium-sized audiences (10K to 300K subscribers) are more likely to be approachable and open to partnerships.
                                Cost vs. Benefit: Higher subscriber counts can lead to higher costs and lower winnability. Assess whether the investment is justified by the potential return, considering the influencers content relevance and audience engagement.
                                Promotion Openness: If the influencer uses affiliate links, mentions paid promotions, or frequently discusses tools in their videos, they are likely open to sponsorships, increasing winnability.
                4. Key Points for evaluation:
                            a. Initial Screening
                                Review the influencers video titles to assess relevance initially. Look for content aligned with <INSERT RELEVANT INFORMATION HERE>
                            b. Deep Dive Analysis
                                Analyze the engagement metrics (views, likes, comments) and content depth by analyzing the full_transcript against the video duration
                                Evaluate how well the influencers content resonates with <INSERT RELEVANT INFORMATION HERE>
                                Thoroughly analyze channel links and video links where the influencer may promote other products or their own social media sites. An influencer using multiple channels of output can increase exposure of {input}
                            c. Ensure to closely assess an influencer's content focus in relation to {input}'s Ideal Customer Profiles (ICPs). Prioritize identifying whether the influencer <INSERT RELEVANT INFORMATION HERE>
                                If an influencer predominantly focuses on a narrow niche, such as <INSERT RELEVANT INFORMATION HERE>, Rate them as irrelevant despite their follower count or potential interest in sponsorships. Additionally, rely more heavily on concrete examples from the content and specific videos to substantiate your evaluations rather than general impressions.
                            d. Prioritize a more thorough alignment check between an influencer's content and our core customer base's needs, particularly regarding the focus on <INSERT RELEVANT INFORMATION HERE>. Ensure that relevance assessments center around whether the influencer's audience comprises <INSERT RELEVANT INFORMATION HERE>. Be cautious not to generalize the appeal of content that emphasizes <INSERT RELEVANT INFORMATION HERE> 
                            e. Ensure a more rigorous evaluation of influencer content by fully considering the implications of their core messaging and its alignment with our targeted audience's preferences. Focus more on whether the influencer actively engages with concepts surrounding <INSERT RELEVANT INFORMATION HERE>. Thoroughly analyzing not just the topics covered but the overarching philosophy that drives the influencer's discussions, ensuring that only channels promoting <INSERT RELEVANT INFORMATION HERE> are considered for partnerships.
                            f. Double-check the calculations and the context of engagement metrics in the evaluation process, reduce reliance on singular metrics.


        """),
        agent=instructions_agent,
        expected_output="Instructions are generated",
        verbose=False,
        context = [research_task, comp_analysis_task]
    )



    write_crew = Crew(agents=[research_agent, comp_analysis_agent, instructions_agent], tasks=[research_task, comp_analysis_task, instructuions_task], process= Process.sequential)

    result = str(write_crew.kickoff())
    footer = """ 
                Use the below JSON-OUTPUT-STRUCTURE as a template for the output.
                JSON-OUTPUT-STRUCTURE:
                {
                    "relevance": {"Evaluation" : "irrelevant | slightly relevant | highly relevant"}, 

                    "impact": {"Evaluation" : "low | medium | high"}, 

                    "winnability": {"Evaluation" : "low | medium | high"}, 

                    "Subscribers": 1000, 
                    
                    "Frequency": {"Evaluation" : "low | medium | high"}, 
                    
                    "Views": {"Evaluation" : "low | medium | high"},
                    
                    "Rationale": "", ;Summary of rationales
                    "partnership_ideas":['...', ...] ;Suggest partnership ideas only if the influencer is highly relevant or slightly relevant. Ignore if irrelevant.
                } """
    return result + footer

