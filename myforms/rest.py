import time
import urllib
import logging
import twitter
import calendar
import datetime as date
import webhelpers.paginate as paginate

from re import findall
from operator import itemgetter, attrgetter

from myforms.models import DBSession
from myforms.models import TwitterStatus, HundredPushups
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

def create(request):
    params  = request.params
    message = params.get('message')
    try:
        entry = HundredPushups()
        entry.create(params)
        if params.get('twitter'):
            _post_twitter_update('%s%s (%s,%s,%s,%s,%s) (Week %s,Day %s,Level %s) %s %s'%(message, entry.total(), entry.set1, entry.set2, entry.set3, entry.set4, entry.exhaust, entry.week, entry.day, entry.level, entry.hashtags, entry.mentions))
    except:
        return { 'status': 404, 'message': 'Failed to Create Entry' }
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
