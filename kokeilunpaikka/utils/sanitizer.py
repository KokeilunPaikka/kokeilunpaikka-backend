import bleach

ALLOWED_TAGS = set(bleach.ALLOWED_TAGS + [
    'a', 'blockquote', 'code', 'del', 'dd', 'dl', 'dt', 'span',
    'h1', 'h2', 'h3', 'h3', 'h4', 'h5', 'h6', 'i', 'img', 'kbd',
    'li', 'ol', 'ul', 'p', 'pre', 's', 'sup', 'sub', 'em', 'u',
    'strong', 'strike', 'ul', 'br', 'hr', 'iframe'
])

ALLOWED_STYLES = set(bleach.ALLOWED_STYLES + [
    'height', 'max-height', 'min-height', 'width', 'max-width', 'min-width'
])

ALLOWED_ATTRIBUTES = {}
ALLOWED_ATTRIBUTES.update(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES.update({
    '*': ['title'],
    'a': ['href', 'target'],
    'img': ['alt', 'src', 'width', 'height', 'align', 'style'],
    'iframe': ['src', 'width', 'height', 'style', 'frameborder', 'allowfullscreen'],
})


def bleach_clean(html):
    """Clean given HTML with bleach.clean()."""
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        styles=ALLOWED_STYLES,
        strip=True
    )
