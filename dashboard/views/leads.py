import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.http import HttpResponse

from accounts.permissions import SalesManagerRequiredMixin
from dashboard.mixins import LoggedActionMixin
from leads.models import Inquiry, Dealer


class InquiryListView(SalesManagerRequiredMixin, View):
    def get(self, request):
        tab    = request.GET.get("type", "all")
        status = request.GET.get("status", "")
        q      = request.GET.get("q", "")
        qs = Inquiry.objects.all()
        if tab in ("contact", "dealer", "architect"):
            qs = qs.filter(type=tab)
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(email__icontains=q)
        return render(request, "dashboard/leads/list.html", {
            "inquiries":    qs,
            "tab":          tab,
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
        elif action == "export_csv":
            return self._export_csv(request)
        return redirect("inquiry_list")

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
