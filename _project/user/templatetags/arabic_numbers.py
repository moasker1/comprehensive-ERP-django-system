from django import template

register = template.Library()

@register.filter(name='arabic_numbers')
def arabic_numbers(value):
    arabic_digits = {'0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤', '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩','.':','}
    return ''.join(arabic_digits.get(char, char) for char in str(value))

@register.filter(name='arabic_days')
def arabic_days(value):
    arabic_days = {'Saturday': 'السبت', 'Sunday': 'الأحد', 'Monday': 'الاثنين', 'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء', 'Thursday': 'الخميس', 'Friday': 'الجمعة'}
    return ''.join(arabic_days.get(char, char) for char in str(value))