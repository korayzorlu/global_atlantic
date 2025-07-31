from PIL import Image
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.urls import reverse
from django.views import View
from qr_code.qrcode.utils import QRCodeOptions

from parts.forms import MakerAddForm, MakerTypeAddForm, ManufacturerAddForm, PartAddForm, PartCompatibilityAddForm, \
    PartManufacturerAddForm, PartSupplierAddForm, RelatedSetAddForm
from parts.helpers import set_value_to_immutable_dict
from parts.models import Maker, MakerDocument, MakerTypeDocument, MakerType, Manufacturer, PartDocument, PartImage, \
    Part, PartCompatibility, PartSupplier, PartManufacturer, RelatedSetImage, RelatedSetDocument, RelatedSet


class MakerDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'parts/maker/maker_data.html', context)


class ManufacturerData(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'parts/manufacturer/manufacturer_data.html', context)


class ManufacturerDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'parts/manufacturer/manufacturer_data.html', context)


class PartDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'parts/part/part_data.html', context)


class RelatedSetDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'parts/related_set/related_set_data.html', context)


class MakerAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        maker_add_form = MakerAddForm()
        context = {
            'maker_add_form': maker_add_form,
        }
        return render(request, 'parts/maker/maker_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        maker_add_form = MakerAddForm(request.POST)
        if maker_add_form.is_valid():
            maker = maker_add_form.save()
            self.handle_files(MakerDocument, {'maker': maker}, 'document')
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("parts:maker_detail", maker.id)
        else:
            context = {
                'maker_add_form': maker_add_form,
            }
            return render(request, 'parts/maker/maker_add.html', context)

    def handle_files(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        files = self.request.FILES.getlist(input_name)
        for file in files:
            file_obj = model(**fields, file=file)
            try:
                file_obj.full_clean()
                file_obj.save()
            except ValidationError as e:
                pass


class MakerEditView(LoginRequiredMixin, View):
    def get(self, request, maker_id, *args, **kwargs):
        maker = get_object_or_404(Maker, pk=maker_id)
        maker_edit_form = MakerAddForm(instance=maker)
        context = {
            'maker': maker,
            'maker_edit_form': maker_edit_form,
        }
        return render(request, 'parts/maker/maker_edit.html', context)

    def post(self, request, maker_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        maker = get_object_or_404(Maker, pk=maker_id)
        maker_edit_form = MakerAddForm(request.POST, instance=maker)
        if maker_edit_form.is_valid():
            maker = maker_edit_form.save()
            self.handle_files(MakerDocument, {'maker': maker}, 'document')
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("parts:maker_detail", maker.id)
        else:
            context = {
                'maker': maker,
                'maker_edit_form': maker_edit_form,
            }
            return render(request, 'parts/maker/maker_edit.html', context)

    def handle_files(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        files = self.request.FILES.getlist(input_name)

        for file in files:
            file_obj = model(**fields, file=file)
            try:
                file_obj.full_clean()
                file_obj.save()
            except ValidationError as e:
                pass


class MakerDetailView(LoginRequiredMixin, View):
    def get(self, request, maker_id, *args, **kwargs):
        maker = get_object_or_404(Maker, pk=maker_id)
        maker_type_add_from = MakerTypeAddForm()
        context = {
            'maker': maker,
            'maker_type_add_from': maker_type_add_from
        }
        return render(request, 'parts/maker/maker_detail.html', context)

    def post(self, request, maker_id, *args, **kwargs):
        maker = get_object_or_404(Maker, pk=maker_id)
        next_url = request.POST.get('next', request.GET.get('next'))
        maker_type_add_from = MakerTypeAddForm(request.POST)
        if maker_type_add_from.is_valid():
            maker_type = maker_type_add_from.save(commit=False)
            maker_type.maker = maker
            maker_type.save()
            # https://stackoverflow.com/a/50384606/14506165
            maker_type_add_from.save_m2m()
            self.handle_files(MakerTypeDocument, {'maker_type': maker_type}, 'document')
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("parts:maker_detail", maker.id)
        else:
            context = {
                'maker_type_add_from': maker_type_add_from,
            }
            return render(request, 'parts/maker/maker_detail.html', context)

    def handle_files(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        files = self.request.FILES.getlist(input_name)

        for file in files:
            file_obj = model(**fields, file=file)
            try:
                file_obj.full_clean()
                file_obj.save()
            except ValidationError as e:
                pass


class MakerDeleteView(LoginRequiredMixin, View):
    """
    Deletes maker permanently
    """

    def get(self, request, maker_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        maker = get_object_or_404(Maker, pk=maker_id)
        maker.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("parts:maker_data")


class MakerDocumentDeleteView(LoginRequiredMixin, View):
    """
    Deletes maker document permanently
    """

    def get(self, request, maker_document_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        maker_document = get_object_or_404(MakerDocument, pk=maker_document_id)
        maker_document.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("dashboard")


class MakerTypeDeleteView(LoginRequiredMixin, View):
    """
    Deletes maker type permanently
    """

    def get(self, request, maker_type_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        maker_type = get_object_or_404(MakerType, pk=maker_type_id)
        maker_type.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("dashboard")


class ManufacturerAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        manufacturer_add_form = ManufacturerAddForm()
        context = {
            'manufacturer_add_form': manufacturer_add_form,
        }
        return render(request, 'parts/manufacturer/manufacturer_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        manufacturer_add_form = ManufacturerAddForm(request.POST)
        if manufacturer_add_form.is_valid():
            manufacturer = manufacturer_add_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("parts:manufacturer_detail", manufacturer.id)
        else:
            context = {
                'manufacturer_add_form': manufacturer_add_form,
            }
            return render(request, 'parts/manufacturer/manufacturer_add.html', context)


class ManufacturerDetailView(LoginRequiredMixin, View):
    def get(self, request, manufacturer_id, *args, **kwargs):
        manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)
        context = {
            'manufacturer': manufacturer,
        }
        return render(request, 'parts/manufacturer/manufacturer_detail.html', context)


class ManufacturerEditView(LoginRequiredMixin, View):
    def get(self, request, manufacturer_id, *args, **kwargs):
        manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)
        manufacturer_edit_form = ManufacturerAddForm(instance=manufacturer)
        context = {
            'manufacturer': manufacturer,
            'manufacturer_edit_form': manufacturer_edit_form,
        }
        return render(request, 'parts/manufacturer/manufacturer_edit.html', context)

    def post(self, request, manufacturer_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)
        manufacturer_edit_form = ManufacturerAddForm(request.POST, instance=manufacturer)
        if manufacturer_edit_form.is_valid():
            manufacturer = manufacturer_edit_form.save()
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("parts:manufacturer_detail", manufacturer.id)
        else:
            context = {
                'manufacturer': manufacturer,
                'manufacturer_edit_form': manufacturer_edit_form,
            }
            return render(request, 'parts/manufacturer/manufacturer_edit.html', context)


class ManufacturerDeleteView(LoginRequiredMixin, View):
    """
    Deletes manufacturer permanently
    """

    def get(self, request, manufacturer_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)
        manufacturer.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("parts:manufacturer_data")


class PartAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        part_add_form = PartAddForm()
        context = {
            'part_add_form': part_add_form,
        }
        return render(request, 'parts/part/part_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        part_add_form = PartAddForm(request.POST)
        if part_add_form.is_valid():
            part = part_add_form.save()
            self.handle_files(PartDocument, {'part': part}, 'document')
            self.handle_images(PartImage, {'part': part}, 'document')
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("parts:part_detail", part.id)
        else:
            context = {
                'part_add_form': part_add_form,
            }
            return render(request, 'parts/part/part_add.html', context)

    def handle_files(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        files = self.request.FILES.getlist(input_name)

        for file in files:
            file_obj = model(**fields, file=file)
            try:
                file_obj.full_clean()
                file_obj.save()
            except ValidationError as e:
                pass

    def handle_images(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        images = self.request.FILES.getlist(input_name)

        for image in images:
            try:
                # check if it is an image
                Image.open(image)
            except IOError:
                continue
            model.objects.create(**fields, image=image)


class PartDetailView(LoginRequiredMixin, View):
    qr_parameters = {"size": 't', "border": 2, "error_correction": 'l', "image_format": "png"}

    def get(self, request, part_id, *args, **kwargs):
        part = get_object_or_404(Part, pk=part_id)
        part_client_url = reverse('parts:part_client', kwargs={'part_uuid': part.uuid})
        part_compatibility_add_form = PartCompatibilityAddForm()
        part_supplier_add_form = PartSupplierAddForm()
        part_manufacturer_add_form = PartManufacturerAddForm()
        context = {
            'part': part,
            'part_client_full_url': request.build_absolute_uri(part_client_url),
            'qr_options': QRCodeOptions(**self.qr_parameters),
            'part_compatibility_add_form': part_compatibility_add_form,
            'part_supplier_add_form': part_supplier_add_form,
            'part_manufacturer_add_form': part_manufacturer_add_form,
        }
        return render(request, 'parts/part/part_detail.html', context)

    def post(self, request, part_id, *args, **kwargs):
        """
        This is a dynamic form control page
        Somebody: Why is it looks like complex?
        - Because it is works dynamic...
        Somebody: It looks too long.
        - It is because of comments and this doc
        Somebody: Why need such a complex code??
        - All of these forms are unbounded from each other
        - All of them uses same kind of treatment
        - Only one of them can be posted to the backend at the same time (they are different forms on the front either)
        - We want to check one of them always (because of one above)
        - We want to return only errors of the form we checked
        - We want to return empty forms with no errors if no existing forms posted
        Somebody: I still don't understand...
        - Then try to write your own code while achieving the goals at the top to understand
        """
        part = get_object_or_404(Part, pk=part_id)
        part_client_url = reverse('parts:part_client', kwargs={'part_uuid': part.uuid})
        # I never want to do this but we need to add part value to the form
        # due to unique together check applied in the form validation
        # and this is the only possible way I found (initial and soft instance not worked)
        request.POST = set_value_to_immutable_dict(request.POST, "part", part)

        # button names: https://stackoverflow.com/a/21505314/14506165
        forms = {
            "part_compatibility_add_form": PartCompatibilityAddForm,
            "part_supplier_add_form": PartSupplierAddForm,
            "part_manufacturer_add_form": PartManufacturerAddForm
        }

        # find the posted form by checking submit button name in the post
        form = None
        for key, value in forms.items():
            if key in request.POST:
                form = {"name": key, "form": value(request.POST)}
                break
        # standard validation
        if form and form["form"].is_valid():
            form["form"].save()
            # redirect to the same page if validation ok
            # to prevent refresh that sends post data again.
            return redirect("parts:part_detail", part.id)
        else:
            # if validation false or no form send, add clean forms except who checked (if exist)
            context = {
                'part': part,
                'part_client_full_url': request.build_absolute_uri(part_client_url),
                'qr_options': QRCodeOptions(**self.qr_parameters),
                'modal_to_show': form["name"] if form else None  # to open the modal of form that got errors
            }
            for key, value in forms.items():
                # if any form checked, then add it with errors
                if form and form["name"] == key:
                    context[key] = form["form"]
                else:
                    # else add the fresh forms to the context
                    context[key] = value()
            return render(request, 'parts/part/part_detail.html', context)


class PartClientView(View):
    def get(self, request, part_uuid, *args, **kwargs):
        part = get_object_or_404(Part, uuid=part_uuid)
        part_info = model_to_dict(part, fields=['description', 'dimensions', 'material'])
        context = {
            'part_info': part_info,
        }
        return render(request, 'parts/part/part_client.html', context)


class PartEditView(LoginRequiredMixin, View):
    def get(self, request, part_id, *args, **kwargs):
        part = get_object_or_404(Part, pk=part_id)
        part_edit_form = PartAddForm(instance=part)
        context = {
            'part_edit_form': part_edit_form,
        }
        return render(request, 'parts/part/part_edit.html', context)

    def post(self, request, part_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        part = get_object_or_404(Part, pk=part_id)
        part_edit_form = PartAddForm(request.POST, instance=part)
        if part_edit_form.is_valid():
            part = part_edit_form.save()
            self.handle_files(PartDocument, {'part': part}, 'document')
            self.handle_images(PartImage, {'part': part}, 'document')
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("parts:part_detail", part.id)
        else:
            context = {
                'part_edit_form': part_edit_form,
            }
            return render(request, 'parts/part/part_edit.html', context)

    def handle_files(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        files = self.request.FILES.getlist(input_name)

        for file in files:
            file_obj = model(**fields, file=file)
            try:
                file_obj.full_clean()
                file_obj.save()
            except ValidationError as e:
                pass

    def handle_images(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        images = self.request.FILES.getlist(input_name)

        for image in images:
            try:
                # check if it is an image
                Image.open(image)
            except IOError:
                continue
            model.objects.create(**fields, image=image)


class PartDeleteView(LoginRequiredMixin, View):
    """
    Deletes part permanently
    """

    def get(self, request, part_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        part = get_object_or_404(Part, pk=part_id)
        part.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("parts:part_data")


class PartCompatibilityDeleteView(LoginRequiredMixin, View):
    """
    Deletes part compatibility permanently
    """

    def get(self, request, part_compatibility_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        part_compatibility = get_object_or_404(PartCompatibility, pk=part_compatibility_id)
        part_compatibility.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("dashboard")


class PartSupplierDeleteView(LoginRequiredMixin, View):
    """
    Deletes part supplier permanently
    """

    def get(self, request, part_supplier_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        part_supplier = get_object_or_404(PartSupplier, pk=part_supplier_id)
        part_supplier.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("dashboard")


class PartManufacturerDeleteView(LoginRequiredMixin, View):
    """
    Deletes part manufacturer permanently
    """

    def get(self, request, part_manufacturer_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        part_manufacturer = get_object_or_404(PartManufacturer, pk=part_manufacturer_id)
        part_manufacturer.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("dashboard")


class PartDocumentDeleteView(LoginRequiredMixin, View):
    """
    Deletes part document permanently
    """

    def get(self, request, part_document_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        part_document = get_object_or_404(PartDocument, pk=part_document_id)
        part_document.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("dashboard")


class PartImageDeleteView(LoginRequiredMixin, View):
    """
    Deletes part image permanently
    """

    def get(self, request, part_image_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        part_image = get_object_or_404(PartImage, pk=part_image_id)
        part_image.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("dashboard")


class RelatedSetAddView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        related_set_add_form = RelatedSetAddForm()
        context = {
            'related_set_add_form': related_set_add_form,
        }
        return render(request, 'parts/related_set/related_set_add.html', context)

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        related_set_add_form = RelatedSetAddForm(request.POST)
        if related_set_add_form.is_valid():
            related_set = related_set_add_form.save()
            self.handle_files(RelatedSetDocument, {'related_set': related_set}, 'document')
            self.handle_images(RelatedSetImage, {'related_set': related_set}, 'document')
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("parts:related_set_detail", related_set.id)
        else:
            context = {
                'related_set_add_form': related_set_add_form,
            }
            return render(request, 'parts/related_set/related_set_add.html', context)

    def handle_files(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        files = self.request.FILES.getlist(input_name)

        for file in files:
            file_obj = model(**fields, file=file)
            try:
                file_obj.full_clean()
                file_obj.save()
            except ValidationError as e:
                pass

    def handle_images(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        images = self.request.FILES.getlist(input_name)

        for image in images:
            try:
                # check if it is an image
                Image.open(image)
            except IOError:
                continue
            model.objects.create(**fields, image=image)


class RelatedSetDetailView(LoginRequiredMixin, View):
    qr_parameters = {"size": 't', "border": 2, "error_correction": 'l', "image_format": "png"}

    def get(self, request, related_set_id, *args, **kwargs):
        related_set = get_object_or_404(RelatedSet, pk=related_set_id)
        related_set_client_url = reverse('parts:related_set_client', kwargs={'related_set_uuid': related_set.uuid})
        context = {
            'related_set': related_set,
            'related_set_client_full_url': request.build_absolute_uri(related_set_client_url),
            'qr_options': QRCodeOptions(**self.qr_parameters),
        }
        return render(request, 'parts/related_set/related_set_detail.html', context)


class RelatedSetClientView(View):
    def get(self, request, related_set_uuid, *args, **kwargs):
        related_set = get_object_or_404(RelatedSet, uuid=related_set_uuid)
        related_set_info = model_to_dict(related_set, fields=['description', 'parts'])
        context = {
            'related_set_info': related_set_info,
        }
        return render(request, 'parts/related_set/related_set_client.html', context)


class RelatedSetEditView(LoginRequiredMixin, View):
    def get(self, request, related_set_id, *args, **kwargs):
        related_set = get_object_or_404(RelatedSet, pk=related_set_id)
        related_set_edit_form = RelatedSetAddForm(instance=related_set)
        context = {
            'related_set_edit_form': related_set_edit_form,
        }
        return render(request, 'parts/related_set/related_set_edit.html', context)

    def post(self, request, related_set_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        related_set = get_object_or_404(RelatedSet, pk=related_set_id)
        related_set_edit_form = RelatedSetAddForm(request.POST, instance=related_set)
        if related_set_edit_form.is_valid():
            related_set = related_set_edit_form.save()
            self.handle_files(RelatedSetDocument, {'related_set': related_set}, 'document')
            self.handle_images(RelatedSetImage, {'related_set': related_set}, 'document')
            if next_url:
                # if next url exist
                return HttpResponseRedirect(next_url)
            else:
                # to prevent refresh that sends post data again.
                return redirect("parts:related_set_detail", related_set.id)
        else:
            context = {
                'related_set_edit_form': related_set_edit_form,
            }
            return render(request, 'parts/related_set/related_set_edit.html', context)

    def handle_files(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        files = self.request.FILES.getlist(input_name)

        for file in files:
            file_obj = model(**fields, file=file)
            try:
                file_obj.full_clean()
                file_obj.save()
            except ValidationError as e:
                pass

    def handle_images(self, model, fields, input_name):
        # https://stackoverflow.com/a/58220917/14506165
        images = self.request.FILES.getlist(input_name)

        for image in images:
            try:
                # check if it is an image
                Image.open(image)
            except IOError:
                continue
            model.objects.create(**fields, image=image)


class RelatedSetDeleteView(LoginRequiredMixin, View):
    """
    Deletes related set permanently
    """

    def get(self, request, related_set_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        related_set = get_object_or_404(RelatedSet, pk=related_set_id)
        related_set.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("parts:related_set_data")


class RelatedSetDocumentDeleteView(LoginRequiredMixin, View):
    """
    Deletes related set document permanently
    """

    def get(self, request, related_set_document_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        related_set_document = get_object_or_404(RelatedSetDocument, pk=related_set_document_id)
        related_set_document.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("dashboard")


class RelatedSetImageDeleteView(LoginRequiredMixin, View):
    """
    Deletes related set image permanently
    """

    def get(self, request, related_set_image_id, *args, **kwargs):
        next_url = request.POST.get('next', request.GET.get('next'))
        related_set_image = get_object_or_404(RelatedSetImage, pk=related_set_image_id)
        related_set_image.delete()

        if next_url:
            # if next url exist
            return HttpResponseRedirect(next_url)
        else:
            return redirect("dashboard")
