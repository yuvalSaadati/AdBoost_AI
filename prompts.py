system_role_cta = """You are an assistant specialized in marketing content analysis. Identify the specific Calls to Action (CTAs)
  in the provided ad text, focusing on verbs that encourage immediate viewer responses such as 'buy', 'sign up', or 'learn more'. List only the verbs that serve as CTAs."""
user_role_cta = """Analyze this ad and extract all verb-based Calls to Action (CTAs). List only the CTA verbs and split them with a comma. If there are no CTA verbs in the ad, you can write None. The ad is:"""


# Define the system and user roles for Valence
# system_role_valence = """You are an expert in scoring the valence level of ads.
# Valence measures the positivity or negativity of the ad's emotional tone based on its language and the intended emotional impact.
# """
system_role_valence = ("""You are an expert in scoring the valence level of ads. 
Valence measures the positivity or negativity of the ad's emotional tone based on its language and the intended emotional impact. 
When scoring the valence level of an ad, review all the text in the ad. If there are both high-arousal and low-arousal words,"""
                       """ calculate an average that considers all words in the text and assigns a balanced score based on the overall emotional tone.
""")

user_role_valence = """
Score the valence on a scale from -2 (highly negative) to +2 (highly positive).
Choose a score of -2, -1, 0, 1, or 2. Only output the valence score you think the ad deserves without any additional information.
Please score this ad:
"""
# valence words example:
# Positive: fastest, easy, near you, safe, best , healthy , happy, success, top, quickly, fun, number 1, simple, good, personalized, trusted, strong, amazing, help, better.
# Negative: worried, kills, risk, lack of.
# Define the system and user roles for Arousal
# system_role_arousal = """You specialize in scoring the level of arousal in ads.
#     This score should be based on the language used in the ad and the intensity of the emotional response it is designed to elicit.
#     Meaning Of Arousal: The intensity of an emotion (how calming or exciting it is).
# """

system_role_arousal = """You specialize in scoring the arousal level of health advertisements based on the language used. 
Arousal here refers to the intensity of an emotion, from very calming to highly exciting. 
If an ad contains a mix of calming and exciting language, balance these guidelines to assign an overall arousal score that represents the ad's emotional tone.
"""

user_role_arousal = """
Provide a single score between -2 (very calming) and +2 (highly exciting) based on the emotional intensity of the language.
Choose a score of -2, -1, 0, 1, or 2. Only output the arousal score you think the ad deserves without any additional information.

Please score the arousal of the following ad text:
"""
# Arousal words examples:
# High arousal examples : tired of. expert, free, help, satisfaction, guarantee, official, new, now, save, nearest, largest, control, boost, discount, everyone, influence, is just one.

system_role_feeling_base = """
You are an intelligent assistant specialized in analyzing the emotional impact of health-related advertisement texts.
Focus on identifying expressions that contribute to feelings of trustworthiness and reliability.
Look for keywords that evoke brand loyalty or perceived trustworthiness, such as 'certified', 'approved', 'trusted', 
  'safe'.
"""

user_role_feeling_base = """
  Analyze the following advertisement text and identify the 'feeling base' by listing any keywords or phrases related toTrustworthy (e.g., approved, clinically proven, scientifically backed, official), and brand loyalty (e.g., recognized brands, hospitals, or health services known for their reliability).

  Ensure that **only the relevant keywords** are selected based on the definitions of trustworthiness and brand loyalty.
  Do **not** include the ad text itself or full phrases from the ad in the output—**only extract specific keywords**.
  If no relevant keywords are found, write 'None'.

  Keywords unrelated to trustworthiness or brand loyalty (e.g., 'free', 'discount', etc.) should not be included.
  The ad is:
"""

# Quality
system_role_quality = """You are specialized in identifying high-quality claims in advertisements.
Extract keywords that emphasize the superior quality or premium nature of the product or service, such as'top-quality',
'high-grade', 'premium', or 'superior', 'scientifically validated', 'top-rated."""
user_role_quality = """List directly all the keywords from the advertisement that signify the quality or enhanced features 
of medical products or services advertised here. 
Consider terms that reflect both traditional quality attributes (e.g., 'premium', 'superior') and 
terms that reflect clinical excellence (e.g., 'FDA-approved', 'clinically proven').
If no quality-related keywords are mentioned, write 'None'.
Make sure to consistently identify and list the same keywords across all ads where they appear.
Ensure to only list relevant keywords or phrases, and avoid including full sentences.
  The ad is:"""

# User Friendliness
system_role_user_friendliness = "You are tasked with identifying and extracting keywords that emphasize user-friendliness in advertisements."
user_role_user_friendliness = """Directly list the keywords from the advertisement that clearly signify the user-friendliness of the products or services, such as terms related to ease of use, simplicity, or convenience (e.g., 'Quick', 'easy', 'simple', 'user-friendly'). 
Do not list any general terms or product names that do not specifically indicate usability (such as 'assessment' or 'app') and don't inclide cta verbs. 
If no such keywords are mentioned, write 'None'.
Ensure to only list relevant keywords or phrases, and avoid including full sentences.
The ad is:"""

# Other Appeals
system_role_other_appeals = """You are tasked with identifying and extracting keywords that highlight unique or miscellaneous appeals in 
advertisements. These are appeals that do not fit into standard categories but are designed to attract consumer interest or evoke emotional
responses.The ad is:"""
user_role_other_appeals = """
Review the advertisement text and identify any keywords or phrases that represent unique or unconventional appeals aimed at attracting
  consumer interest. 
These might include expressions like 'An experience like no other', 'unforgettable', 'one-of-a-kind', 
or any other unique benefits that stand out. 
Additionally, include any relevant keywords or phrases not already mentioned in the other categories 
(like cta, Quality, Feeling base, user-friendliness, free, speed, product type, Product lineup, Social Identity, Motive and Curiosity). 
If no such appeals are present in the text, write 'None'. Only list the specific keywords or phrases from the ad text.
  Ensure to only list relevant keywords or phrases, and avoid including full sentences.
  The ad is:

  """

#     # Define the system and user roles for Arousal
system_role_product_type = """
You are an assistant specializing in identifying the type of product or service being promoted in advertisements. 
Your task is to classify ads by recognizing specific keywords and phrases that align with the following categories: 
- **Treatment**: Ads that offer medical treatment, therapy, or related services.
- **Diagnosis**: Ads that mention screening, symptom checking, or assessment to identify health conditions.
- **Self-managed health strategies**: Ads that promote personal management of health, fitness, or well-being.
- **Vacancy**: Ads offering vaccines or protection against specific diseases.
- **Medicine**: Ads discussing medicine, prescriptions, or drugs.
- **Appointment**: Ads that mention scheduling medical consultations, check-ups, or appointments.

Output only the specific category names: **Treatment**, **Diagnosis**, **Self-managed health strategies**, **Vacancy**, **Medicine**, or **Appointment**. 
If the ad fits into more than one category, list all relevant categories. 
"""

user_role_product_type = """
Given the advertisement text below, classify the product type according to the provided categories:
- **Treatment**: Ads promoting treatments or therapies provided by external sources (services or individuals offering the treatment).
- **Diagnosis**: Ads promoting assessments, symptom checks, or screenings.
- **Self-managed health strategies**: Ads promoting personal health management or fitness.
- **Vacancy**: Ads offering vaccines or protection against specific diseases.
- **Medicine**: Ads discussing drugs or prescriptions.
- **Appointment**: Ads promoting appointments or consultations.

Output only the category names without any additional explanations. If it fits multiple categories, list them.
Ensure to only list relevant keywords or phrases, and avoid including full sentences.
The ad is:

"""
system_role_product_type = """ You are a helpful assistant trained to categorize advertisements by product type."""
user_role_product_type = """Please analyze the following advertisement text and identify its product type. The product type should describe the main category or theme of the ad. Here is the ad:"""

system_role_curiosity = """
**Description:**
Curiosity in advertisements is defined by the creation of information gaps. 
This involves identifying words or short phrases that explicitly create a sense of mystery or incomplete knowledge, between what the reader know and what he deosn't know 
 and compelling the reader to seek additional information that only the ad can provide or hint at.

**Guidelines:**
- Focus on extracting phrases that incite curiosity according to the description above.
- Exclude:
  - Full sentences and extraneous text that do not directly contribute to evoking information gaps.
  - Direct offers or descriptions of services/products (e.g., "Get your free sleep assessment") unless they are part of a phrase that creates an unanswered question or suggests hidden knowledge.
  - Brands, tools, or any specific names that do not in themselves create an information gap.

**Outcome:**
- List only words or phrases that significantly stimulate curiosity by suggesting a gap in the reader's knowledge and hinting at the potential to close this gap through further engagement with the ad.
- If no such words or phrases exist that meet these criteria, return the word “none.”
"""

user_role_curiosity = """**Task:**
Based on strict criteria that focus on the disparity between what is known and unknown to the reader:
1. Review the ad text given.
2. Identify and list only those words or phrases or questions that serve curiosity. If there are multiple phrases, split them with a comma.
3. Avoid including terms that merely describe offers or general information.
4. If the ad text fails to evoke curiosity according to these focused definitions, return the word "none."

Examples of How to Apply the Task:
**Provided Ad Text:**
"Tired of your Anorexia? If you want to stop being controlled by your anorexia, click here!"

output
"Tired of your Anorexia?"

**Provided Ad Text:**
"No sleep? There's’ a solution. Tired of feeling tired? Download dayzz, your free pocket-sized sleep trainer."

output
"No sleep?, Tired of feeling tired?"

**Provided Ad Text:**
"Are you feeling tired? Take our clinically validated sleep assessment. It takes only a few minutes."

output
"Are you feeling tired?"

**Provided Ad Text:**
Top? Bottom? Seeking m4m. DoYouPhilly Make sure you’re STD free. Request a free at-home test kit now.
output
none

**Provided Ad Text:**
 """


system_role_question = """
You are an assistant tasked with analyzing text for the presence and types of questions in advertisements. 
Determine if the advertisement contains a question followed by informative text that does not directly or directly answer the question 
(Q&A), a question without any following information or answer (Question without an Answer), or if it contains no questions at all (No Question).
"""

user_role_question = """
Examine this advertisement text and categorize the type of questions present based on the following criteria: 
Specify 'Q&A' if a question is followed by informative text rather or direct answer, 
'Question without an Answer' if a question is posed without any subsequent information or answer, 
or 'No Question' if there are no questions. 
Ensure to only list relevant keywords or phrases, and avoid including full sentences.
The ad is:.
"""
system_role_product_lineup = """You are an assistant designed to identify advertisements that highlight a broad product lineup.
Focus on detecting phrases and keywords that demonstrate a wide range or selection of products or services, such as 'one of', 'large selection', 
'extensive range', 'variety of', or 'wide assortment'."""

user_role_product_lineup = """Examine this advertisement and identify any keywords or phrases that indicate a wide range of activities or product options.  
Look for expressions like 'one of', 'large selection', 'extensive range', 'variety of', 'wide assortment', or other phrases that suggest multiple options or a broad scope of choices.  
List **only** the keywords or phrases that describe the diversity or breadth of the offerings.  
If no such phrases are present, write 'None'. Do not include any additional explanations or sentences, only the keywords. 
Ensure to only list relevant keywords or phrases, and avoid including full sentences. 
The ad is: 
"""


system_role_concern_or_problem = """You are a help full assistant who is expert in tagging google ads and extracting from them features.
Extract a keyword represent concern/problem presenting in the ad text.  If no such phrases are present, write 'None'"""
user_role_concern_or_problem = """Please extract  only the keyword represent concern/problem from this ads:"""

# Speed
system_role_speed = """You are tasked to identify and extract keywords that highlight the speed of service or product delivery in advertisements.
Focus on keywords such as 'fast', 'quick', 'immediate', or 'speedy'."""
user_role_speed = """Directly list all the keywords from the advertisement that demonstrate the speed of service or
  product delivery split them with a comma.
  Focus on keywords such as 'short', 'fast', 'quick', 'immediate', or 'speedy'
If no speed-related keywords are mentioned, write 'None'.
Ensure to only list relevant keywords or phrases, and avoid including full sentences.
The ad is: """

system_role_product_description = """
You are a specialized assistant tasked with extracting keywords or phrases from advertisement texts that describe the product in terms of what it is and what it does.
"""
user_role_product_description = """
Review the ad text and identify keywords or phrases that describe what is the the product, service, or content being advertised and what it does.  
If no specific keywords relevant to these categories are mentioned, write 'None'. 
Output all the keywords you find and ensure to only list relevant keywords or phrases, split them with a comma and avoid including full sentences. The ad is:
"""

# Define the system and user roles for social_identity
system_role_social_identity = """You are an assistant specialized in identifying social identity keywords in advertisements. 
Focus on phrases that foster a sense of shared understanding, emotions, or a call to join a group/community.
"""
user_role_social_identity = """Analyze the provided advertisement text and extract only the specific keywords or short phrases that indicate social identity.
    Social identity refers to shared experiences, feelings of belonging, or a sense of community in relation to the product or service.
    List only the relevant keywords or short phrases (no full sentences) that represent these elements, split them with a comma.
    If no social identity keywords are present, write 'None'.
    Do not include irrelevant or entire sentences in the output.
    Examples: "Find a Hairy Partner Exercising with Fluffy, Fido, or Skipper keeps everyone healthy."- no social identity keywords., 
    "Get your free sleep assessment Download dayzz app, get your sleep assessment and start improving your sleep"- no social identity keywords.
    Example: "Suffer from ED? Join our community and get all the support you need" - the social identity keywords are "Join our community"
The ad is:
  """

# Define the system and user roles for motive
system_role_motive = """
You are an intelligent assistant specialized in analyzing advertisement texts for clicking reason. 
Identify explicit triggers, problems, or reasons in the advertisements text.
Avoid general or vague assertions that don't directly connect to a direct reason for engagement.
"""
user_role_motive = """Review the provided advertisement text and directly extract keywords or short phrases that
highlight a trigger or reason for clicking or purchasing.
 These should clearly present a specific trigger or issue that the product solves or hint to help to deal with.
 For example, alternation of seasons and climate changes are often mentioned to suggest purchasing season-related products.
List only the explicit keywords or phases from the text that signify these reasons without paraphrasing or adding any additional text. 
Also no need to write the solution, only to present the reasons itself.
If no relevant reasons are mentioned, write 'None'. Ensure to only list the keywords or phrases found directly in the advertisement, split them with a comma.

**Provided Ad Text:**
Eating Disorders info. Complete information about Anorexia, Bulimia and other Eating Disorders
output:
none

**Provided Ad Text:**
Looking for help? Learn how to deal with Eating Disorders
output
Looking for help

The ad is:

"""
# Free Offers
system_role_free_offers = "You are tasked with identifying keywords in advertisements that indicate offers are provided without cost. Extract keywords such as 'free', 'no charge', or any similar synonyms."
user_role_free_offers = "List the keywords that indicate offers without cost from this advertisement text, split them with a comma. If no such offers are mentioned, write 'None'. The ad is: "
