from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """템플릿에서 딕셔너리 키로 값을 가져오는 필터"""
    return dictionary.get(key)