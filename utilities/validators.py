from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


# https://stackoverflow.com/a/38179816/14506165
class ExtensionValidator(RegexValidator):
    def __init__(self, extensions, message=None):
        if not hasattr(extensions, '__iter__'):
            extensions = [extensions]
        regex = '\.(%s)$' % '|'.join(extensions)
        if message is None:
            message = _('File type not supported. Accepted types are: %(extensions)s.') % {
                'extensions': ', '.join(extensions)
            }
        super(ExtensionValidator, self).__init__(regex=regex, message=message, code='invalid_regex')

    def __call__(self, value):
        super(ExtensionValidator, self).__call__(value.name.lower())
