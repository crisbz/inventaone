from django.http import JsonResponse
from django.template.loader import render_to_string

class AjaxFormMixin:
    """
    Mixin para manejar formularios con AJAX,
    soporta creación y edición según si hay 'pk' en kwargs.
    """

    def form_valid(self, form):
        # Asigna usuario creador solo si es creación (no tiene pk)
        if hasattr(form.instance, 'uc') and not form.instance.pk:
            form.instance.uc = self.request.user
        # Siempre asigna usuario modificador
        if hasattr(form.instance, 'um'):
            form.instance.um = self.request.user
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            # Si pk existe, es edición: carga instancia
            self.object = self.get_object()
            form = self.form_class(instance=self.object)
        else:
            # Crear: formulario vacío
            form = self.form_class()
        context = {'form': form}
        html_form = render_to_string(self.template_name, context, request=request)
        return JsonResponse({'success': False, 'html_form': html_form})

    def post(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            # Edición: instancia para actualizar
            self.object = self.get_object()
            form = self.form_class(request.POST, instance=self.object)
        else:
            # Crear: formulario sin instancia
            form = self.form_class(request.POST)
        if form.is_valid():
            self.object = form.save()
            return JsonResponse({'success': True})
        else:
            context = {'form': form}
            html_form = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'success': False, 'html_form': html_form})

""""""
#esto es para editar un objeto existente con AJAX
"""""
    def form_valid(self, form):
        form.instance.um = self.request.user  # Usuario que modifica
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(instance=self.object)
        context = {'form': form}
        html_form = render_to_string(self.template_name, context, request=request)
        return JsonResponse({'success': False, 'html_form': html_form})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        if form.is_valid():
            form.instance.um = request.user  # Usuario que modifica
            form.save()
            return JsonResponse({'success': True})
        else:
            context = {'form': form}
            html_form = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'success': False, 'html_form': html_form})
        

    esto es para crear un objeto nuevo con AJAX
    def form_valid(self, form):
        form.instance.uc = self.request.user  # Usuario que crea
        form.instance.um = self.request.user  # Usuario que modifica (primera vez es el mismo)
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        html_form = render_to_string(self.template_name, context, request=request)
        return JsonResponse({'success': False, 'html_form': html_form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # Asigna los usuarios antes de guardar
            form.instance.uc = request.user
            form.instance.um = request.user
            form.save()
            return JsonResponse({'success': True})
        else:
            context = {'form': form}
            html_form = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'success': False, 'html_form': html_form})
        
"""