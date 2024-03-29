import time
import urllib
import logging
import twitter
import calendar
import datetime as date
import webhelpers.paginate as paginate

from re import findall
from operator import itemgetter, attrgetter
from subprocess import call

from myforms.models import DBSession
from myforms.models import TwitterStatus, HundredPushups, Fundraiser
from myforms.helpers import *

Log = logging.getLogger(__name__)


def listing(request):
    Log.debug('listing')
    """ json data for deals """
    params       = request.params
    currentPage  = int(params.get('page') or 1)
    itemsPerPage = int(params.get('rp')   or 30)
    sortName     = params.get('sortname')  or 'dealEndDate'
    sortOrder    = params.get('sortorder') or 'desc'
    query        = params.get('query')
    type         = params.get('qtype')  or ''
    qrange       = params.get('range')  or ''
    form         = params.get('format') or None
    if query:
        relObjs = HundredPushups().getList()
        page    = paginate.Page(relObjs, page=currentPage, items_per_page=itemsPerPage)
        total   = page.item_count
    else:
        offset  = (currentPage - 1) * itemsPerPage
        relObjs = HundredPushups().getSet(itemsPerPage, offset)
        total   = HundredPushups().getTotal()
        page    = paginate.Page(relObjs, page=1, items_per_page=itemsPerPage)
    result      = { }
    result['rows']  = [ ]
    result['page']  = currentPage
    result['total'] = total
    for item in page.items:
        row = {'id': item.id, 'cell': ['<a style="color: blue;text-decoration: underline;" href="#" class="pushups view_entry" id="view_%s" title="View">%s</a>'%(item.id, item.id)]}
        row['cell'].append(item.week)
        row['cell'].append(item.day)
        row['cell'].append(item.level)
        if not form:
            row['cell'].append(item.set1)
            row['cell'].append(item.set2)
            row['cell'].append(item.set3)
            row['cell'].append(item.set4)
            row['cell'].append(item.set5)
            row['cell'].append(item.set6)
            row['cell'].append(item.set7)
            row['cell'].append(item.exhaust)
        row['cell'].append(item.total())
        if not form:
            row['cell'].append(item.createdDate.strftime(getSettings('date.long')))
        row['cell'].append('<img class="pushups edit_entry" alt="Edit Entry" title="Edit Entry" src="/static/images/edit.png" id="edit_%s" />&nbsp;<img class="pushups delete_entry" alt="Delete Entry" title="Delete Entry" src="/static/images/delete.png" id="delete_%s" />'%(item.id, item.id))
        result['rows'].append(row)
    return result

def reporting(request):
    Log.debug('reporting')
    """ json data for entry objects """
    label   = 'Entries'
    data    = { }
    list    = [ ]
    labels  = [ ]
    objects = _message_sql_query(request.params)
    if request.params.has_key('range'):
        label = request.params.get('range')
    for item in objects:
        created = calendar.timegm(item.createdDate.timetuple()) * 1000
        list.append([created, item.total()])
        labels.append({'title': 'Week %s, Day %s, Level %s'%(item.week, item.day, item.level), 'hashtags': item.hashtags, 'mentions': item.mentions, 'permalink': 'https://twitter.com/#!/useEvil/status/110958709164875776'})
    data ={
        'label':  label,
        'labels': labels,
        'data':   list
    }
#    Log.debug('==== data [%s]'%(data))
    _init_twitter()
    return [data]

def reports(request):
    x = request.matchdict['x']
    y = request.matchdict['y']
    params = request.params
    query  = params.get('query')
    type   = params.get('qtype') or ''
    if query:
        relObjs = Release().getAll(query, type)
    else:
        relObjs = Release().getAll()
    list = [ ]
    for object in relObjs:
        value = getattr(object, y)
        list.append([object.createdDate.strftime(getSettings('date.short')), value])
    data = {
        'label': y.title(),
        'data': list
    }
    return data

def orders(request):
    orders = Fundraiser().getByCreatedDate()
    list   = { 'candy1': [], 'candy2': [], 'candy3': [], 'candy4': [], 'candy5': [], 'candy6': [], 'candy7': [], 'candy8': [], 'candy9': [], 'candy10': [], 'candy11': [], 'candy12': [], 'candy13': [] }
    print '==== orders [%s]'%(orders)
    for order in orders:
        list['candy1'].append([order.createdDate.strftime(getSettings('date.short')), order.candy1])
        list['candy2'].append([order.createdDate.strftime(getSettings('date.short')), order.candy2])
        list['candy3'].append([order.createdDate.strftime(getSettings('date.short')), order.candy3])
        list['candy4'].append([order.createdDate.strftime(getSettings('date.short')), order.candy4])
        list['candy5'].append([order.createdDate.strftime(getSettings('date.short')), order.candy5])
        list['candy6'].append([order.createdDate.strftime(getSettings('date.short')), order.candy6])
        list['candy7'].append([order.createdDate.strftime(getSettings('date.short')), order.candy7])
        list['candy8'].append([order.createdDate.strftime(getSettings('date.short')), order.candy8])
        list['candy9'].append([order.createdDate.strftime(getSettings('date.short')), order.candy9])
        list['candy10'].append([order.createdDate.strftime(getSettings('date.short')), order.candy10])
        list['candy11'].append([order.createdDate.strftime(getSettings('date.short')), order.candy11])
        list['candy12'].append([order.createdDate.strftime(getSettings('date.short')), order.candy12])
        list['candy13'].append([order.createdDate.strftime(getSettings('date.short')), order.candy13])
    data   = [
        {
            'label': "Truffles (#902)",
            'data': list['candy1']
        },
        {
            'label': "Assorted Chocolates (#318)",
            'data': list['candy2']
        },
        {
            'label': "Milk Chocolates (#326)",
            'data': list['candy3']
        },
        {
            'label': "Dark Chocolates (#330)",
            'data': list['candy4']
        },
        {
            'label': "Nuts & Chews (#334)",
            'data': list['candy5']
        },
        {
            'label': "Toffee-ettes (#316)",
            'data': list['candy6']
        },
        {
            'label': "Peanut Brittle (#355)",
            'data': list['candy7']
        },
        {
            'label': "Assorted Molasses Chips (#360)",
            'data': list['candy8']
        },
        {
            'label': "Peppermints (#358)",
            'data': list['candy9']
        },
        {
            'label': "Gourmet Lollypops (#296)",
            'data': list['candy10']
        },
        {
            'label': "Jolly Snowman Box (#9127)",
            'data': list['candy11']
        },
        {
            'label': "Mini Holiday Fancy Box (#596)",
            'data': list['candy12']
        },
        {
            'label': "Gift Certificate (#767)",
            'data': list['candy13']
        }
    ]
    print '==== data [%s]'%(data)
    return data

def new(request):
    params  = request.params
    print '==== params [%s]'%(params)
    try:
        order = Fundraiser()
        order.create(params)
    except:
        return { 'status': 404, 'message': 'Failed to Create New Order' }
    call("/Users/useevil/Documents/Playground/bin/notifo.pl -message=\"%s bought candy for Bree's Fundraiser.\" -title=\"2012 Fundraiser for Bree\""%(params['name']), shell=True)
    return { 'status': 200, 'message': 'Successfully Created New Order' }

def create(request):
    params  = request.params
    message = params.get('message')
    try:
        entry = HundredPushups()
        entry.create(params)
    except:
        return { 'status': 404, 'message': 'Failed to Create Entry' }
    try:
        if params.get('twitter'):
            _post_twitter_update('%s%s (%s,%s,%s,%s,%s,%s,%s,%s) (Week %s,Day %s,Level %s) %s %s'%(message, entry.total(), entry.set1, entry.set2, entry.set3, entry.set4, entry.set5, entry.set6, entry.set7, entry.exhaust, entry.week, entry.day, entry.level, entry.hashtags, entry.mentions))
    except:
        return { 'status': 404, 'message': 'Failed to Create Twitter Entry' }
    return { 'status': 200, 'message': 'Successfully Created Entry' }

def view(request):
    id = request.matchdict['id']
    try:
        entry = HundredPushups().getById(id)
    except:
        return { 'status': 404, 'message': 'Failed to Get Entry' }
    return { 'status': 200, 'entry': _jsonify_data(entry) }

def edit(request):
    id     = request.matchdict['id']
    params = request.params
    try:
        entry = HundredPushups().getById(id)
        entry.update(params)
    except:
        return { 'status': 404, 'message': 'Failed to Edit Entry' }
    return { 'status': 200, 'message': 'Successfully Edit Entry' }

def delete(request):
    id = request.matchdict['id']
    try:
        entry = HundredPushups().getById(id)
        entry.delete()
    except:
        return { 'status': 404, 'message': 'Failed to Delete Entry' }
    return { 'status': 200, 'message': 'Successfully Delete Entry' }

def paid(request):
    id = request.matchdict['id']
    try:
        order = Fundraiser().getById(id)
        order.paid = 1
    except:
        return { 'status': 404, 'message': 'Failed to Update Order' }
    return { 'status': 200, 'message': 'Successfully Update Order' }

def error(request):
    return { 'status': request.matchdict['id'], 'message': 'You Do Not have permissions to Approve Release Ticket' }

def _jsonify_data(data):
    hash = {
        'id': data.id,
        'week': data.week,
        'day': data.day,
        'level': data.level,
        'set1': data.set1,
        'set2': data.set2,
        'set3': data.set3,
        'set4': data.set4,
        'set5': data.set5,
        'set6': data.set6,
        'set7': data.set7,
        'exhaust': data.exhaust,
        'hashtag': data.hashtags,
        'mentions': data.mentions,
        'permalink': data.permalink,
        'message': data.message,
        'createdDate': data.createdDate.strftime(getSettings('date.short')),
    }
    return hash

def _message_sql_query(params=None):
    start   = params.get('start')
    end     = params.get('end')
    query   = params.get('query')
    type    = params.get('qtype') or ''
    results = None
    if end and start:
        start, end = getStartEnd(start, end, 'long')
    if start and not end:
        start, end = getStartEnd(start, None, 'long')
    if end and not start:
        start, end = getStartEnd(None, end, 'long')
    results  = HundredPushups().getByCreatedDate(start, end, query, type)
    return results

def _post_twitter_update(status=None):
    if not status: return
    print 'Sending to Twitter...'
    api = _init_twitter()
    status = api.PostUpdate(status)

def _init_twitter():
    try:
        api = twitter.Api(
                consumer_key=getSettings('twitter.consumer_key'),
                consumer_secret=getSettings('twitter.consumer_secret'),
                access_token_key=getSettings('twitter.access_token_key'),
                access_token_secret=getSettings('twitter.access_token_secret')
            )
    except:
        return
    return api
