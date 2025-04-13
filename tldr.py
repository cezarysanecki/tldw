from article_content import ArticleContentExtractor
from article_summarizer import ArticleContentSummarizer


def summarize_article(url):
    article_content_extractor = ArticleContentExtractor(url)
    article_metadata = article_content_extractor.run()
    title = article_metadata['title']
    content = article_metadata['content']

    article_content_summarizer = ArticleContentSummarizer()
    article_info = article_content_summarizer.summarize(title, content)
    title = article_info['title']
    paragraph = article_info['paragraph']
    paragraph_pl = article_info['paragraph_pl']

    return {
        "title": title,
        "summary": paragraph,
        "summary_pl": paragraph_pl
    }
