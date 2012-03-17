import logging
import datetime as date
import myforms.helpers as h

from myforms.models import DBSession
from myforms.models import TwitterStatus, HundredPushups, Fundraiser
from myforms.models import MyModel

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response

log = logging.getLogger(__name__)

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
    if not request.matchdict.has_key('year'):  return
    if not request.matchdict.has_key('start'): return
    if not request.matchdict.has_key('end'):   return
    if request.params.has_key('id') and request.params.get('id'):
        id = request.params.get('id')
        log.debug('==== id [%s]'%(id))
        try:
            order = Fundraiser().getById(id)
            order.paid = 1
        except:
            log.debug('==== failed to set paid for id [%s]'%(id))
    child  = request.matchdict['child']
    year   = request.matchdict['year']
    start  = date.datetime.strptime(request.matchdict['start'], h.getSettings('date.short'))
    end    = date.datetime.strptime(request.matchdict['end'], h.getSettings('date.short'))
    orders = Fundraiser().getByCreatedDate(start, end)
    total  = Fundraiser().getTotalsData(start, end)
    grand  = Fundraiser().total_price(total[0])
    data   = { 'h': h, 'orders': orders, 'total': total[0], 'grand_total': grand, 'onsale': end >= date.datetime.today() }
    return render_to_response('templates/fundraiser/'+child+'-'+year+'.pt', data, request=request)

def reports(request):
    return { 'h': h }

def view(request):
    if not request.matchdict.has_key('id'): return
    release = Release().getById(request.matchdict['id'])
    return { 'release': release, 'h': h }

def edit(request):
    return { 'h': h }
