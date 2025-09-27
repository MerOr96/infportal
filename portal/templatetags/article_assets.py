from django import template

register = template.Library()

CATEGORY_ICONS = {
    'tehnologii': 'bi-cpu',
    'obrazovanie': 'bi-mortarboard',
    'karernoe-razvitie': 'bi-bar-chart-line',
    'zdorove': 'bi-heart-pulse',
    'gorodskaya-sreda': 'bi-buildings',
}

ARTICLE_ILLUSTRATIONS = {
    'kak-kompanii-v-rossii-vnedryayut-iskusstvennyi-intellekt-v-2024-godu': 'portal/images/illustrations/ai-lab.svg',
    'kak-razvivat-cifrovye-navyki-sotrudnikov-opyt-universitetov-i-korporacii': 'portal/images/illustrations/learning-hub.svg',
    'pyat-shagov-dlya-perehoda-na-rukovodyashchuyu-poziciyu': 'portal/images/illustrations/leadership-steps.svg',
    'kak-ofisnye-privychki-vliyayut-na-zdorove-i-produktivnost': 'portal/images/illustrations/wellbeing-space.svg',
    'gorodskie-soobshchestva-kak-draiver-razvitiya-raionov': 'portal/images/illustrations/city-community.svg',
    'kak-postroit-personalnuyu-strategiyu-obucheniya-na-god': 'portal/images/illustrations/productivity-flow.svg',
}

DEFAULT_ILLUSTRATION = 'portal/images/illustrations/default-story.svg'
DEFAULT_ICON = 'bi-journal-text'


@register.filter
def category_icon(category):
    """Return Bootstrap icon class for a category instance or slug."""
    slug = ''
    if category:
        slug = getattr(category, 'slug', category)
    return CATEGORY_ICONS.get(slug, DEFAULT_ICON)


@register.filter
def article_illustration(article):
    """Return relative static path for article illustration."""
    slug = ''
    if article:
        slug = getattr(article, 'slug', article)
    return ARTICLE_ILLUSTRATIONS.get(slug, DEFAULT_ILLUSTRATION)
