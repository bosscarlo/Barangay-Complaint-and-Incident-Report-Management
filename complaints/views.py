from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import Complaint, ComplaintAttachment, ComplaintUpdate, Category
from .forms import ComplaintForm, ComplaintUpdateForm


@login_required
def dashboard(request):
    user = request.user
    complaints = Complaint.objects.all() if user.is_staff_member else Complaint.objects.filter(complainant=user)
    stats = {
        'total': complaints.count(),
        'pending': complaints.filter(status='pending').count(),
        'in_progress': complaints.filter(status__in=['under_review', 'in_progress']).count(),
        'resolved': complaints.filter(status='resolved').count(),
        'urgent': complaints.filter(priority='urgent').count(),
    }
    category_data = complaints.values('category__name').annotate(count=Count('id')).order_by('-count')[:5]
    return render(request, 'complaints/dashboard.html', {
        'stats': stats,
        'recent_complaints': complaints[:8],
        'category_data': category_data,
    })


@login_required
def complaint_list(request):
    user = request.user
    qs = Complaint.objects.all() if user.is_staff_member else Complaint.objects.filter(complainant=user)
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    type_ = request.GET.get('type', '')
    search = request.GET.get('q', '')
    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    if type_:
        qs = qs.filter(type=type_)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
    return render(request, 'complaints/list.html', {
        'complaints': qs,
        'status_choices': Complaint.STATUS_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
        'type_choices': Complaint.TYPE_CHOICES,
        'filters': {'status': status, 'priority': priority, 'type': type_, 'q': search},
    })


@login_required
def complaint_create(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.complainant = request.user
            complaint.save()
            f = request.FILES.get('attachments')
            if f:
                ComplaintAttachment.objects.create(complaint=complaint, file=f, filename=f.name)
            messages.success(request, f'Report submitted! Tracking #: {complaint.id:05d}')
            return redirect('complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintForm()
    return render(request, 'complaints/form.html', {'form': form, 'action': 'Submit'})


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if not request.user.is_staff_member and complaint.complainant != request.user:
        return HttpResponseForbidden()
    update_form = None
    if request.user.is_staff_member:
        if request.method == 'POST':
            update_form = ComplaintUpdateForm(request.POST)
            if update_form.is_valid():
                update = update_form.save(commit=False)
                update.complaint = complaint
                update.updated_by = request.user
                update.old_status = complaint.status
                new_status = update_form.cleaned_data.get('new_status')
                if new_status:
                    update.new_status = new_status
                    complaint.status = new_status
                    if new_status == 'resolved':
                        complaint.resolved_at = timezone.now()
                    complaint.save()
                update.save()
                messages.success(request, 'Update added!')
                return redirect('complaint_detail', pk=pk)
        else:
            update_form = ComplaintUpdateForm()
    return render(request, 'complaints/detail.html', {
        'complaint': complaint,
        'update_form': update_form,
        'updates': complaint.updates.all(),
        'attachments': complaint.attachments.all(),
    })


@login_required
def complaint_edit(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if complaint.complainant != request.user and not request.user.is_staff_member:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            complaint = form.save()
            f = request.FILES.get('attachments')
            if f:
                ComplaintAttachment.objects.create(complaint=complaint, file=f, filename=f.name)
            messages.success(request, 'Report updated!')
            return redirect('complaint_detail', pk=pk)
    else:
        form = ComplaintForm(instance=complaint)
    return render(request, 'complaints/form.html', {'form': form, 'action': 'Update', 'complaint': complaint})