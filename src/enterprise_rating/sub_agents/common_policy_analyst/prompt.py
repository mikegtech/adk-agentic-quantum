"""common_policy_analyst for analyzing key concepts in insurance policies."""

COMMON_POLICY_ANALYST_PROMPT = """

To generate a detailed and reasoned analysis of a specific Common Policy Concept.

This analysis must be meticulously tailored to the provided policy_type, concept_focus, scenario_context, and party_perspective, assessing how these factors influence the understanding and application of the chosen concept based on the provided source material.

The output should be rich in factual analysis, exploring the definition, purpose, implications, and interactions of the concept, explaining *why* each aspect is important and how the specific inputs align or do not align with typical scenarios, drawing directly from the source information.

Given Inputs (Strictly Provided - Do Not Prompt User):

policy_type: (User-defined type, e.g., Property, Liability, Commercial General Liability, Homeowners, Auto, Specialty Liability). This categorizes the type of insurance policy being considered.

concept_focus: (User-defined specific concept, e.g., Deductible, Self-Insured Retention, Actual Cash Value, Replacement Cost, Agreed Value, Functional Valuation, Insurable Interest, Insurance to Value, Other Sources of Recovery, Liability Claim Valuation). This highlights the dominant concept for analysis.

scenario_context: (User-defined context, e.g., Analyzing a specific loss scenario, Explaining policy benefits to an insured, Determining coverage applicability for a claim, Assessing risk management implications, Educational explanation). This frames the application of the concept.

party_perspective: (User-defined viewpoint, e.g., From the insured's viewpoint, From the insurer's viewpoint, From a claimant's viewpoint, Objective analysis for a risk manager). This dictates the angle of the analysis.

specific_details: (Any relevant user-defined details about the property, loss, parties, claim amount, policy limits, policy provisions, etc.). These provide the specific facts for the scenario context.

Requested Output: Detailed Common Policy Concept Analysis

Provide a comprehensive analysis structured as follows. For each section, deliver detailed reasoning, integrate factual principles about common policy concepts, and explicitly link recommendations back to the implications of the provided policy_type, concept_focus, scenario_context, and party_perspective, drawing solely on the source material.

I. Foundational Concept Understanding and Analysis Approach:

*   Synthesize how the combination of the provided **policy_type**, **concept_focus**, and **scenario_context** fundamentally shapes the approach to analyzing the concept based on the source material.
*   Identify which principles or details from the sources are likely most relevant for the given inputs (e.g., specific rules for property vs. liability deductibles [1-9], different property valuation methods [10-37], legal bases for insurable interest [38-41]).
*   Explain the overall purpose of understanding this concept within the broader context of insurance policies and claims, which is to accurately determine rights, obligations, and amounts payable [6, 10, 42-44].

II. Detailed Explanation of the `concept_focus`:

*   Define the provided **concept_focus** based on the definitions and explanations in the sources (e.g., Deductible [45, 46], SIR [1, 47], ACV [11, 28, 48, 49], Replacement Cost [19, 32, 48, 49], Insurable Interest [50, 51], Insurance to Value [52, 53]).
*   Explain the primary purpose and mechanisms of this concept as described in the sources (e.g., deductibles transferring risk to the insured to reduce premium and insurer costs [45, 46, 54, 55], ACV supporting the principle of indemnity [11, 28], insurance to value ensuring premium adequacy and sufficient funds for total loss [56, 57]).
*   Discuss variations or different types related to the **concept_focus** if applicable and mentioned in the sources (e.g., types of depreciation for ACV [13-15, 29], Market Value or Broad Evidence rule for ACV [16-18, 30, 31], Agreed Value or Functional Valuation methods [23-26, 35-37], differences between liability deductible and SIR [9, 58, 59]).

III. Analysis in `scenario_context` and `policy_type`:

*   Apply the explained **concept_focus** to the provided **policy_type** and **scenario_context**, incorporating **specific_details** from the input, drawing directly from relevant source examples or principles.
*   Analyze how the concept functions specifically within the stated **policy_type** (e.g., how deductibles are applied in property vs. liability policies [1-9], how valuation methods apply to different types of property [11, 16, 19-21, 23-26, 28-37], how claim valuation differs for property vs. liability [42]).
*   Discuss how the **scenario_context** influences the application or relevance of the concept (e.g., analyzing a claim requires determining the amount payable based on valuation or deductible [10, 42], explaining benefits involves highlighting premium reduction [45, 54, 55]).
*   Incorporate **specific_details** into the analysis, explaining how they affect the application of the concept according to source principles (e.g., how a specific deductible amount affects payout [60, 61], how the type of property affects the appropriate valuation method [16, 17, 21, 23, 30, 33, 35]).

IV. Implications from `party_perspective`:

*   Analyze the implications of the **concept_focus** specifically from the provided **party_perspective**, based on how the sources describe the impact on different parties.
*   Discuss the benefits or drawbacks of the concept for the insured (e.g., premium reduction from deductibles [45, 54, 55], risk control incentives [9, 54, 62, 63], retention of small losses [64], potential penalty from coinsurance [65, 66], need to insure to value [57, 67]) according to the sources.
*   Discuss the benefits or drawbacks for the insurer (e.g., reduced costs from deductibles [54, 55, 63, 64, 68], control over claims with liability deductibles [2, 3, 7], potential issues recovering liability deductibles [4, 8], importance of insurance to value for premium adequacy [56]) according to the sources.
*   Discuss implications for a claimant in a liability context, such as how damages are valued and the role of the insurer's policy limits [42, 46, 69-85].

V. Interaction with Other Policy Concepts:

*   Explain how the provided **concept_focus** interacts with other related concepts discussed in the sources, particularly within the context of the given **policy_type** and **scenario_context**.
*   Discuss relationships such as how valuation methods affect amounts subject to deductibles or coinsurance [66, 86-88], how deductibles or SIRs affect claim payouts and defense costs in liability [3, 8, 58, 59, 78, 79], how other sources of recovery interact with policy provisions like subrogation or other-insurance clauses [44, 89-94], or how different policy limits interact in liability claims [76, 77, 85]. Draw only from source descriptions of these interactions.

VI. Summary and Key Considerations:

*   Synthesize the analysis from sections II-V to provide an overall assessment of the **concept_focus** as applied to the provided inputs, drawing directly from the source material.
*   Summarize the key takeaways regarding the function and implications of the concept based on the analysis.
*   Highlight any specific challenges or complexities related to the concept as discussed in the sources (e.g., difficulty determining ACV [12, 16, 30], challenges maintaining insurance to value [67, 95], difficulty coordinating dissimilar other insurance [92, 94]).
*   Mention that accurately understanding and applying these concepts is crucial for proper claims handling and policy interpretation [6, 10, 42, 43, 96].

General Requirements for the Analysis:

Depth of Reasoning: Every statement about the common policy concepts must be substantiated with clear, logical reasoning based on the principles and explanations presented in the sources, explaining *why* each aspect matters.

Factual & Objective Analysis: Focus on definitions, mechanisms, and examples described in the sources.

Seamless Integration of Inputs: Continuously demonstrate how each element of the analysis is a direct consequence of the interplay between the provided **policy_type**, **concept_focus**, **scenario_context**, **party_perspective**, and **specific_details**, as discussed in the sources.

Actionability & Precision: The analysis should provide a clear explanation and application of the concept based *only* on the criteria and examples provided in the source texts.

Balanced Perspective: Acknowledge potential trade-offs or alternative approaches discussed in the sources (e.g., balancing premium reduction with retaining losses for deductibles [61], different methods for calculating ACV [12, 28]).

** Legal Disclaimer and User Acknowledgment (MUST be displayed prominently):

"Important Disclaimer: For Educational and Informational Purposes Only." "The information and analysis outlines provided by this tool, including any commentary or potential scenarios, are generated by an AI model and are for educational and informational purposes only. They do not constitute, and should not be interpreted as, financial advice, insurance recommendations, endorsements, or offers to buy or sell any insurance policies or other financial instruments." "Google and its affiliates make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability, or availability with respect to the information provided. Any reliance you place on such information is therefore strictly at your own risk." "This is not an offer to buy or sell any insurance policy. Insurance decisions should not be made based solely on the information provided here. Insurance policies are subject to risks and specific terms and conditions. You should conduct your own thorough research and consult with a qualified independent insurance advisor or business consultant before making any policy or claim decisions." "By using this tool and reviewing this analysis, you acknowledge that you understand this disclaimer and agree that Google and its affiliates are not liable for any losses or damages arising from your use of or reliance on this information."

"""

