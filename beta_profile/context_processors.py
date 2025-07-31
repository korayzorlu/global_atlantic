from beta_profile.models import Currency


def currencies(request):
    return {
        #'currencies': Currency.get_currencies(base='TRY'),
    }
