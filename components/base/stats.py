from django_components import component


@component.register("stats")
class Stats(component.Component):
    template_name = 'base/stats.html'

    def get_context_data(self, stats):
        return {"stats": stats}
