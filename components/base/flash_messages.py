from django_components import component


@component.register('flash_messages')
class FlashMessages(component.Component):
    template_name = 'base/flash_messages.html'

    def get_context_data(self, messages):
        return {'messages': messages}
