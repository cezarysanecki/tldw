from article_content import ArticleContentExtractor
from article_summarizer import ArticleContentSummarizer


def summarize_article(url):
    article_content_extractor = ArticleContentExtractor(url)
    article_metadata = article_content_extractor.run()

    article_content_summarizer = ArticleContentSummarizer
    article_content_summarizer.summarize(article_metadata['article_title'], article_metadata['article_content'])

    title = article_content_summarizer['title']
    paragraph = article_content_summarizer['paragraph']
    paragraph_pl = article_content_summarizer['paragraph_pl']

    return {
        "success": True,
        "error": "",
        "title": title,
        "summary": paragraph,
        "summary_pl": paragraph_pl
    }
