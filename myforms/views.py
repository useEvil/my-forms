import datetime as date
import myforms.helpers as h

from myforms.models import DBSession
from myforms.models import TwitterStatus, HundredPushups, Fundraiser
from myforms.models import MyModel

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response

def my_view(request):
    root = DBSession().query(MyModel).filter(MyModel.name==u'root').first()
    return { 'root': root, 'h': h, 'project':'my-forms' }

def index(request):
    range  = ''
    end    = date.datetime.today().strftime(h.getSettings('date.short'))
    start  = (date.datetime.today() - date.timedelta(days=30)).strftime(h.getSettings('date.short'))
    recent = HundredPushups().getRecent()
    if request.params.has_key('start') and request.params.get('start'):
        start = request.params.get('start')
        if not request.params.has_key('end'):
            start, end = h.getStartEnd(start, None)
    if request.params.has_key('end') and request.params.get('end'):
        end = request.params.get('end')
        if not request.params.has_key('start'):
            start, end = h.getStartEnd(None, end)
    if request.params.has_key('range') and request.params.get('range'):
        range = request.params.get('range')
        if range == 'Last60Days':
            days = 60
        elif range == 'Last90Days':
            days = 90
        elif range == 'Last30Days':
            days = 30
        else:
            days = 7
        end   = date.datetime.today().strftime(h.getSettings('date.short'))
        start = (date.datetime.today() - date.timedelta(days=days)).strftime(h.getSettings('date.short'))
        start, end = h.getStartEnd(start, end)
    return { 'h': h, 'start': start, 'end': end, 'type': type, 'range': range, 'recent': recent }

def iphone(request):
    recent = HundredPushups().getRecent()
    return { 'h': h, 'recent': recent }

def fundraiser(request):
    if not request.matchdict.has_key('child'): return
    if not request.matchdict.has_key('start'): return
    if not request.matchdict.has_key('end'):   return
    start = date.datetime.strptime(request.matchdict['start'], h.getSettings('date.short'))
    end   = date.datetime.strptime(request.matchdict['end'], h.getSettings('date.short'))
    orders = Fundraiser().getByCreatedDate(start, end)
    total  = Fundraiser()
    total.candy1  = Fundraiser().getTotals(orders, 'candy1')
    total.candy2  = Fundraiser().getTotals(orders, 'candy2')
    total.candy3  = Fundraiser().getTotals(orders, 'candy3')
    total.candy4  = Fundraiser().getTotals(orders, 'candy4')
    total.candy5  = Fundraiser().getTotals(orders, 'candy5')
    total.candy6  = Fundraiser().getTotals(orders, 'candy6')
    total.candy7  = Fundraiser().getTotals(orders, 'candy7')
    total.candy8  = Fundraiser().getTotals(orders, 'candy8')
    total.candy9  = Fundraiser().getTotals(orders, 'candy9')
    total.candy10 = Fundraiser().getTotals(orders, 'candy10')
    total.candy11 = Fundraiser().getTotals(orders, 'candy11')
    total.candy12 = Fundraiser().getTotals(orders, 'candy12')
    total.candy13 = Fundraiser().getTotals(orders, 'candy13')
    return { 'h': h, 'orders': orders, 'total': total }

def reports(request):
    return { 'h': h }

def view(request):
    if not request.matchdict.has_key('id'): return
    release = Release().getById(request.matchdict['id'])
    return { 'release': release, 'h': h }

def edit(request):
    return { 'h': h }
