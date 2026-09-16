import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.http import HttpResponse

from accounts.permissions import SalesManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from formbuilder.models import FormDefinition
from leads.models import Inquiry, Dealer

# Inquiries submitted outside the form builder (currently just the
# code-managed Collection Inquiry Form) carry no `form` FK — this is the
# tab/group key used to select them.
UNTRACKED_FORM_KEY = "collection"


class InquiryListView(SalesManagerRequiredMixin, View):
    def get(self, request):
        tab    = request.GET.get("type", "all")
        status = request.GET.get("status", "")
        q      = request.GET.get("q", "")

        forms = list(
            FormDefinition.objects.filter(target_pipeline=FormDefinition.TARGET_INQUIRY).order_by("name")
        )
        tabs = [{"key": f.slug, "label": f.name} for f in forms]
        tabs.append({"key": UNTRACKED_FORM_KEY, "label": "Collection Inquiry Form"})

        qs = Inquiry.objects.select_related("form").all()
        if tab == UNTRACKED_FORM_KEY:
            qs = qs.filter(form__isnull=True)
        elif tab != "all":
            qs = qs.filter(form__slug=tab)
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(email__icontains=q)

        # Group by form for display; stable sort preserves the -created order within each group.
        inquiries = list(qs.order_by("-created"))
        inquiries.sort(key=lambda inq: inq.form_label)

        return render(request, "dashboard/leads/list.html", {
            "inquiries":    inquiries,
            "tab":          tab,
            "tabs":         tabs,
            "status_filter": status,
            "q":            q,
            "STATUS_CHOICES": Inquiry.STATUS_CHOICES,
            "active_nav":   "leads",
        })

    def post(self, request):
        action = request.POST.get("action", "")
        if action == "update_status":
            inq = get_object_or_404(Inquiry, pk=request.POST.get("pk"))
            inq.status = request.POST.get("status", inq.status)
            inq.notes  = request.POST.get("notes", inq.notes)
            inq.save()
            messages.success(request, "Status updated.")
            return redirect("inquiry_list")
        elif action == "export_csv":
            return self._export_csv(request)
        elif action == "bulk_update_status":
            return self._bulk_update_status(request)
        elif action == "bulk_delete":
            return self._bulk_delete(request)
        return redirect("inquiry_list")

    def _redirect_with_filters(self, request):
        tab    = request.POST.get("tab", "all")
        status = request.POST.get("status_filter", "")
        q      = request.POST.get("q", "")
        url = reverse("inquiry_list") + f"?type={tab}"
        if status:
            url += f"&status={status}"
        if q:
            url += f"&q={q}"
        return redirect(url)

    def _bulk_update_status(self, request):
        ids    = request.POST.getlist("ids")
        status = request.POST.get("status", "")
        valid  = dict(Inquiry.STATUS_CHOICES)
        if ids and status in valid:
            Inquiry.objects.filter(pk__in=ids).update(status=status)
            messages.success(request, f"Updated {len(ids)} inquiry(ies) to '{valid[status]}'.")
        elif not ids:
            messages.error(request, "No inquiries selected.")
        return self._redirect_with_filters(request)

    def _bulk_delete(self, request):
        ids = request.POST.getlist("ids")
        if ids:
            deleted, _ = Inquiry.objects.filter(pk__in=ids).delete()
            messages.success(request, f"Deleted {len(ids)} inquiry(ies).")
        else:
            messages.error(request, "No inquiries selected.")
        return self._redirect_with_filters(request)

    def _export_csv(self, request):
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="inquiries.csv"'
        writer = csv.writer(resp)
        writer.writerow(["id", "type", "name", "email", "phone", "city", "status", "created"])
        for inq in Inquiry.objects.all():
            writer.writerow([
                inq.pk, inq.type, inq.name, inq.email,
                inq.phone, inq.city, inq.status, inq.created,
            ])
        return resp


class DealerListView(SalesManagerRequiredMixin, View):
    def get(self, request):
        qs = Dealer.objects.all()
        q  = request.GET.get("q", "")
        state = request.GET.get("state", "")
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(city__icontains=q)
        if state:
            qs = qs.filter(state__icontains=state)
        return render(request, "dashboard/leads/dealer_list.html", {
            "dealers":    qs,
            "q": q, "state": state,
            "active_nav": "leads",
        })


class DealerCreateView(SalesManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request):
        return render(request, "dashboard/leads/dealer_form.html", {"active_nav": "leads"})

    def post(self, request):
        d = request.POST
        dealer = Dealer.objects.create(
            name=d["name"], contact=d.get("contact", ""),
            email=d.get("email", ""), phone=d.get("phone", ""),
            city=d["city"], state=d.get("state", ""),
            address=d.get("address", ""),
            lat=d.get("lat") or None, lng=d.get("lng") or None,
            status=d.get("status", "active"),
        )
        self.log_action("Created dealer", dealer)
        messages.success(request, f"Dealer '{dealer.name}' added.")
        return redirect("dealer_list")


class DealerEditView(SalesManagerRequiredMixin, LoggedActionMixin, View):
    def get(self, request, pk):
        dealer = get_object_or_404(Dealer, pk=pk)
        return render(request, "dashboard/leads/dealer_form.html", {
            "dealer": dealer, "active_nav": "leads"
        })

    def post(self, request, pk):
        dealer = get_object_or_404(Dealer, pk=pk)
        d = request.POST
        dealer.name    = d["name"]
        dealer.contact = d.get("contact", "")
        dealer.email   = d.get("email", "")
        dealer.phone   = d.get("phone", "")
        dealer.city    = d["city"]
        dealer.state   = d.get("state", "")
        dealer.address = d.get("address", "")
        dealer.lat     = d.get("lat") or None
        dealer.lng     = d.get("lng") or None
        dealer.status  = d.get("status", "active")
        dealer.save()
        self.log_action("Updated dealer", dealer)
        messages.success(request, "Dealer updated.")
        return redirect("dealer_list")
