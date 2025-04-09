from openai import OpenAI

from utils.cache import ensure_cache_dir, create_cache_json, reuse_cache_json


class ArticleContentSummarizer:
    def __init__(self):
        ensure_cache_dir()

        self.client = OpenAI()
        self.messages = []

    def summarize(self, article_title, article_content):
        print("=== SUMMARIZING ARTICLE ===")

        result = reuse_cache_json(f'{article_title}_response')
        if result:
            return result

        paragraph = self.__ask_assistant_persisting(
            f"Summarize this article given its content into increasing levels of conciseness. Begin by summarizing it into a single paragraph.\nTitle: {article_title}\nContent: \n```{article_content}```\n\nDo not describe or mention the article itself. Simply summarize the points it makes. Focus on the overall or underlying takeaway, cause, reason, or answer BEYOND what's already in the title and description, which is already shown to the user. PROVIDE NO OTHER OUTPUT OTHER THAN THE PARAGRAPH.")
        # sentence = self.__ask_assistant_persisting(
        #     "Now summarize it into a single sentence. Focus on the overall or underlying takeaway, cause, reason, or answer BEYOND what's already in the title and description, which is already shown to the user. Basically, provide a single sentence answer to the question the video poses. PROVIDE NO OTHER OUTPUT OTHER THAN THE SENTENCE.")
        # question = self.__ask_assistant_persisting(
        #     f'Rephrase the video title into a single motivating question. Focus on the overall TOPIC or SUBJECT of the video. This could be just the video title verbatim, especially if it is already a question. Don\'t use information outside of the video title. For example, if the title is "This problem ...", the question would be "What problem ...?". As a reminder, here is the video title again: "{video_title}". PROVIDE NO OTHER OUTPUT OTHER THAN THE QUESTION.')
        # word = self.__ask_assistant_persisting(
        #     'Answer the question we just asked with just a single phrase, ideally one or two words. Examples: "Is EVOLUTION REAL?" -> "Yes." "Have scientists achieved fusion?" -> "No." "It depends." "Will AI take over the world?" -> "Nobody knows." "Why NO ONE lives here" -> "Poor geography." "Inside Disney\'s $1 BILLION disaster" -> "No market need." "Scientists FEAR this one thing" -> "Climate change." "Why is there war in the middle east?" -> "It\'s complicated." "Have we unlocked the secret to QUANTUM COMPUTING?" -> "Not really." "A day from Hell" -> "1999 Moore tornado" ... -> "Mostly." ... -> "Usually." PROVIDE NO OTHER OUTPUT OTHER THAN THE WORD(S) OF THE ANSWER.')
        # search_term = self.__ask_assistant_persisting(
        #     'Now suggest a search term for a Wikipedia search that replaces watching the video. Make the search SPECIFIC to the TOPIC of the video. For example: "The $6 Billion Transit Project with No Ridership" -> "FasTracks"; "Why NOBODY lives in this part of China" -> "Gobi Desert"; "This unknown professor REVOLUTIONIZED ..." -> "Joseph-Louis Lagrange"; "Every Computer Can Be Hacked!" -> "Zero-Day Vulnerability"; Provide the Wikipedia page name with no special punctuation:')
        paragraph_pl = self.__ask_assistant_persisting(
            f"Translate below text from English to Polish. Under no circumstances DO NOT change content, just provide translation.\n---\n{paragraph}")

        response = {
            'title': article_title,
            'paragraph': paragraph,
            'paragraph_pl': paragraph_pl,
            # 'sentence': sentence,
            # 'question': question,
            # 'word': f'{word} ({search_term})',
            # 'wikipedia': 'https://en.wikipedia.org/w/index.php?search=' + quote_plus(search_term)
        }

        create_cache_json(f'{article_title}_response', response)

        return response

    def __ask_assistant_persisting(self, instruction):
        self.messages.append(
            {
                "role": "user",
                "content": instruction
            }
        )
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            store=True,
            messages=self.messages,
        )
        answer = completion.choices[0].message.content
        self.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )
        print(answer)
        return answer
