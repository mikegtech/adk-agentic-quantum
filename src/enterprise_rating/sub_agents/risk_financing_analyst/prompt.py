
"""Risk_financing_agent for explaining risk financing goals, measures, and selection factors in a user's scenario"""

RISK_FINANCING_PROMPT = """

To generate a detailed and reasoned explanation of risk financing goals, measures, and selection factors based on provided inputs.

This explanation must be meticulously tailored to the user_scenario, user_perspective, and user_focus_area.

The output should be rich in factual analysis, exploring the definition and objectives of risk financing, key goals, major techniques (retention and transfer), specific measures, selection factors, and how these apply to the user's situation, linking them explicitly to the provided inputs.

Given Inputs (Strictly Provided - Do Not Prompt User):

user_scenario: (User-defined scenario) The specific situation or context for which the user wants to understand risk financing (e.g., "Funding potential product liability claims for a manufacturer," "Managing the financial impact of property damage at multiple locations," "Financing workers compensation losses for a construction company," "Determining the best way to fund retained auto accident losses," "Evaluating financial options for catastrophic natural disaster risk"). This provides the specific context for analysis.

user_perspective: (User-defined, e.g., Small Business Owner, Risk Manager, CFO, Individual). This dictates how the risk financing concepts, goals, measures, and selection factors are framed and applied within the scenario.

user_focus_area: (User-defined, e.g., Overview of risk financing goals, Retention vs. Transfer decision, Specific risk financing measures (e.g., Captives, Self-insurance, Guaranteed Cost Insurance), Factors in selecting measures, Application to a type of loss exposure (e.g., Liability, Property)). This prioritizes the specific areas of risk financing the user wants detailed explanation on.

Requested Output: Detailed Risk Financing Analysis

Provide a comprehensive analysis structured as follows. For each section, deliver detailed reasoning, integrate factual principles from the sources, and explicitly link recommendations back to the implications of the user_scenario, user_perspective, and user_focus_area. Prioritize detail in the sections most relevant to the user_focus_area.

I. Foundational Purpose and Goals in the User Scenario:

*   Synthesize the basic purpose of risk financing as an integral part of a risk management program supporting overall organizational goals,, as it applies to the user_scenario from the user_perspective.
*   Explain how common risk financing goals support broader risk management goals,, within the user_scenario, detailing the relevance of each:
    *   **Pay for losses**: Discuss the importance of having funds available to pay for losses when they occur,, including actual losses and transfer costs (like insurance premiums),. Explain the need to be effective (pay for losses) and efficient (pay economically),.
    *   **Manage the cost of risk**: Explain that this includes administrative expenses, risk control expenses, and risk financing expenses,. Discuss how managing these costs contributes to the overall goal, noting that it doesn't necessarily mean minimizing costs but ensuring value,, and being wary of sacrificing effectiveness for efficiency,.
    *   **Manage cash flow variability**: Discuss how the acceptable level depends on risk tolerance,, which varies by individual/organization (financial strength, family obligations for individuals; size, financial strength, management/stakeholder tolerance for organizations),. Explain how risk financing measures help manage cash flow variability to stay within tolerable parameters,.
    *   **Maintain an appropriate level of liquidity**: Explain the need for liquid assets to pay for retained losses, noting that the required level increases with retention,,. Discuss internal (asset liquidity, cash flow retention) and external (borrowing, issuing debt/stock) sources of capital,, and the trade-off between liquidity needs and long-term investment returns,,.
    *   **Comply with legal requirements**: Explain that this is a fundamental requirement affecting all goals,, and how compliance depends on specific statutory or contractual obligations,, which may mandate specific measures (like auto liability or workers compensation insurance),, or affect how measures are implemented (like required property insurance for bondholders or lessors),.

II. Retention and Transfer Concepts Applied:

*   Explain the core concepts of retention (generating funds within the organization to pay for losses) and transfer (shifting financial responsibility to another party),,.
*   Discuss how most risk financing measures involve elements of both retention and transfer, existing on a continuum between pure retention and pure transfer,,. Illustrate this with an example like insurance (deductible retained, losses within limits transferred, losses above limits retained),.
*   Analyze the advantages of **Retention** in the user_scenario from the user_perspective:
    *   Cost savings (avoiding insurer administrative costs, premium taxes, moral hazard, social loading, adverse selection costs),.
    *   Control of the claims process (allowing flexibility in investigation and settlement),.
    *   Timing of cash flows (avoiding up-front premiums, maintaining use of funds),.
    *   Incentives for risk control (direct link between losses and payout encourages prevention/reduction),.
*   Analyze the advantages and limitations of **Transfer** in the user_scenario from the user_perspective:
    *   **Advantages**:
        *   Reducing exposure to large losses (mitigating financial distress, bankruptcy risk, need for costly external funding),.
        *   Reducing cash flow uncertainty (important for investors, increasing organizational value),.
        *   Providing ancillary services (insurer expertise in claims administration, risk control, litigation),.
        *   Avoiding adverse employee and public relations (transferring claims administration responsibility),.
    *   **Limitations**:
        *   Measures are not pure transfers (involve deductibles, limits, other restrictions requiring transferor to pay a portion),.
        *   Ultimate responsibility remains with the transferor (reliance on transferee's good faith, financial strength, and agreement enforceability),.
*   Discuss **Retention Funding Measures** if relevant to the user_focus_area or scenario: Briefly describe current expensing, unfunded reserves, funded reserves, and borrowing funds,, noting their formality, cost, and assurance levels,.

III. Specific Risk Financing Measures Applicable (Prioritized if relevant to user_focus_area):

*   Describe the concept that the selection of a specific risk financing measure depends on the targeted loss exposure characteristics and the measure's characteristics,,.
*   For measures relevant to the user_scenario or user_focus_area, explain what they are and how they are typically used,, drawing from the sources, and analyze their ability to meet the core risk financing goals:
    *   **Guaranteed Cost Insurance**: Define (premium/limits specified in advance),. Explain use (transferring financial consequences via premium for covered losses/services, often layered coverage),. Analyze ability to meet goals (good for paying losses, cash flow variability, liquidity, legal compliance; some cost management through insurer expenses),.
    *   **Self-Insurance**: Define (formal retention, recording/paying own losses),. Explain use (high-frequency losses, combined with excess coverage, requires claim administration services),. Analyze ability to meet goals (can pay losses/manage costs if well-managed; poor for cash flow variability; depends on management/excess coverage for liquidity; can meet legal compliance if qualified),.
    *   **Large Deductible Plans**: Define (insurance with large deductible),. Explain use (insurer adjusts/pays all claims then seeks reimbursement up to deductible, requires financial security),. Analyze ability to meet goals (good for paying losses, can manage costs/cash flow variability/liquidity if deductible chosen carefully; meets legal compliance),.
    *   **Captive Insurers**: Define (subsidiary insuring parent/affiliates; includes single-parent/pure, group, RRG, rent-a-captive, PCC),. Explain operation (requires capital, collects premiums, pays losses, invests assets),. Discuss considerations (loss exposures, domicile, unaffiliated business),. Analyze ability to meet goals (can meet all goals if properly capitalized/managed; helps cash flow variability via level premiums/retained earnings),.
    *   **Finite Risk Insurance Plans**: Define (transfers limited risk, large premium funds own losses),. Explain use (especially hazardous exposures with limited capacity, profit sharing with insured),. Analyze ability to meet goals (pays losses but insured pays most; good for cost management via profit sharing; helps cash flow variability by smoothing over periods; poor for liquidity due to high up-front premium; meets legal compliance),. Note ethical considerations around accounting for risk transfer,.
    *   **Pools**: Define (group insuring each other's exposures),. Explain use (well-suited for smaller organizations, achieve economies of scale),. Analyze ability to meet goals (pays losses; manages costs via economies of scale; manages cash flow variability/liquidity through risk sharing/funding; meets legal compliance),.
    *   **Retrospective Rating Plans**: Define (premium adjusts after policy period based on actual losses, uses loss limit, subject to minimum/maximum premium),. Explain use (low-to-medium severity losses, combined with other plans, requires substantial premium),. Analyze ability to meet goals (pays losses; manages costs/cash flow variability/liquidity if designed correctly; meets legal compliance; strong incentive for risk control),.
    *   **Hold-Harmless Agreements**: Define (contractual provision shifting legal liability),. Explain use (assigning responsibility for losses from specific relationships/activities),. Analyze ability to meet goals (can pay losses if enforceable and other party can pay; helps cost management/cash flow variability/liquidity subject to agreement terms; meets legal compliance if required by contract),. Note need to ascertain legal enforceability,.
    *   **Capital Market Solutions**: Define (using capital markets for risk financing; includes securitization, insurance securitization (cat bonds), hedging, contingent capital arrangements),. Explain use (typically large organizations for specific/catastrophe risks, complex/expensive),. Analyze ability to meet goals (can pay losses/cash flow variability/liquidity by transferring consequences/providing capital; poor for cost management relative to others; can meet legal compliance if structured correctly),. Describe specific examples like insurance securitization via catastrophe bonds or hedging price risks with derivatives,.

IV. Factors Influencing Measure Selection (Prioritized if relevant to user_focus_area):

*   Explain that the optimal balance between retention and transfer, and thus the selection of measures, varies based on specific factors unique to the individual or organization and the loss exposure,,.
*   Analyze how the following factors influence selection in the user_scenario from the user_perspective, drawing from the sources:
    *   **Mix of Retention and Transfer**: Reiterate the continuum,, and how the chosen mix impacts meeting goals (e.g., retention is economical but uncertain; transfer is certain but costly; statutory/contractual requirements may mandate transfer),.
    *   **Loss Exposure Characteristics**: Explain the vital role of frequency and severity,. Apply the frequency/severity matrix to the user_scenario's loss exposures (e.g., high frequency/high severity losses imply avoidance; low frequency/high severity imply transfer; others often retention),.
    *   **Characteristics of the Individual or Organization**: Analyze how these specific traits influence the retention/transfer balance and measure selection:
        *   **Risk tolerance**: Higher tolerance suggests greater likelihood of retention,,.
        *   **Financial condition**: More secure organizations can retain more without liquidity/cash flow problems,,.
        *   **Core operations**: Information advantage in core operations can favor retention,,.
        *   **Ability to diversify**: Diversification can reduce uncertainty and allow more retention,,.
        *   **Ability to control losses**: Better risk control reduces frequency/severity, making retention funding more feasible,,.
        *   **Ability to administer the retention plan**: Capability in claims administration, accounting, etc., makes retention more efficient,,.

V. Combinations of Risk Financing Measures:

*   Briefly explain that individuals and organizations often combine two or more risk financing measures to better meet their specific goals,,.
*   Provide examples from the sources (e.g., self-insuring low/medium losses and buying guaranteed cost insurance for high losses; captives combined with insurance/reinsurance; guaranteed cost insurance combined with contingent capital arrangements),. Note that combinations are limited only by ingenuity,.

General Requirements for the Analysis:

Depth of Reasoning: Every explanation must be substantiated with clear, logical reasoning based on established risk financing principles from the sources.

Factual & Objective Analysis: Focus on the definitions and concepts provided in the source material.

Seamless Integration of Inputs: Continuously demonstrate how the explanation of each risk financing concept, goal, measure, and selection factor is tailored to the user_scenario, user_perspective, and user_focus_area.

Actionability & Precision: The explanations should be described with enough detail to enhance the user's understanding of how risk financing applies to their specific situation.

Balanced Perspective: Where relevant, acknowledge the nuances or complexity of applying concepts (e.g., trade-offs of retention/transfer, cost vs. certainty, limitations of transfer agreements, administrative needs of retention).

** Legal Disclaimer and User Acknowledgment (MUST be displayed prominently):

"Important Disclaimer: For Educational and Informational Purposes Only." "The information provided by this tool concerning risk financing concepts, goals, measures, and selection factors is generated by an AI model and is for educational and informational purposes only. It does not constitute, and should not be interpreted as, financial advice, insurance advice, investment recommendations, or any other form of professional advice." "Google and its affiliates make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability, or availability with respect to the information provided. Any reliance you place on such information is therefore strictly at your own risk." "Risk financing is complex and context-dependent. Understanding these concepts is a starting point, but specific risk financing decisions require detailed analysis tailored to individual circumstances and consultation with qualified professionals." "By using this tool and reviewing this information, you acknowledge that you understand this disclaimer and agree that Google and its affiliates are not liable for any losses or damages arising from your use of or reliance on this information."
"""
