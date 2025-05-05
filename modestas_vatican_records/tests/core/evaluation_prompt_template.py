MAX_SCORE = "5"

# From on https://huggingface.co/learn/cookbook/rag_evaluation
EVALUATION_PROMPT = """###Task Description:
An instruction (might include an Input inside it), a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given.
1. Write a detailed feedback that assess the quality of the response strictly based on the given score rubric, not evaluating in general.
2. After writing a feedback, write a score that is an integer between 1 and 5. You should refer to the score rubric.
3. The output format should look as follows: \"Feedback: {{write a feedback for criteria}} [RESULT] {{an integer number between 1 and 5}}\"
4. Please do not generate any other opening, closing, and explanations. Be sure to include [RESULT] in your output.

###The instruction to evaluate:
{instruction}

###Response to evaluate:
{response}

###Reference Answer (Score 5):
{reference_answer}

###Score Rubrics:
[Is the response correct, accurate, and factual based on the reference answer?]
Score 1: The response is completely incorrect, inaccurate, and/or not factual.
Score 2: The response is mostly incorrect, inaccurate, and/or not factual.
Score 3: The response is somewhat correct, accurate, and/or factual.
Score 4: The response is mostly correct, accurate, and factual.
Score 5: The response is completely correct, accurate, and factual.

###Feedback:"""

FEEDBACK_GENERALIZATION_PROMPT = """###Task Description:
I have collected a big chunk of feedback messages regarding the evaluation of a specific task.
Please read through the following feedback and provide a generalized summary that highlights the key themes, common strengths, and areas for improvement.
Your summary should be concise, clear, and capture the overall sentiment and constructive points mentioned in the feedback.
Please do not generate any other opening, closing, and explanations.
The feedback summary should be written in a single paragraph.

###Feedback to summarize:
{feedback}
"""
