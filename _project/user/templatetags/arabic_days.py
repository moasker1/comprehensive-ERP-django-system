from django import template

register = template.Library()

@register.filter(name='arabic_days')
def arabic_days(value):
    arabic_days = {'6': 'السبت', '0': 'الأحد', '1': 'الاثنين', '2': 'الثلاثاء', '3': 'الأربعاء', '4': 'الخميس', '5': 'الجمعة'}
    return ''.join(arabic_days.get(char, char) for char in str(value))