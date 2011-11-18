from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from sqlalchemy import engine_from_config

from myforms.models import initialize_sql

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    session_factory = UnencryptedCookieSessionFactoryConfig('abetterplacetoshop')
    config = Configurator(settings=settings, session_factory = session_factory)
    config.add_static_view('static', 'myforms:static')
    config.add_route('index', '/', view='myforms.views.index', view_renderer='templates/index.pt')
    config.add_route('reports', '/reports', view='myforms.views.reports', view_renderer='templates/reports.pt')
    config.add_route('iphone', '/iphone', view='myforms.views.iphone', view_renderer='templates/iphone/index.pt')
    config.add_route('fundraiser', '/fundraiser', view='myforms.views.fundraiser', view_renderer='templates/fundraiser.pt')
    # JSON REST
    config.add_route('rest_listing', '/REST/forms/listing', view='myforms.rest.listing', renderer='json', request_method='GET')
    config.add_route('rest_reporting', '/REST/forms/reporting', view='myforms.rest.reporting', renderer='json', request_method='GET')
    config.add_route('rest_create', '/REST/forms/create', view='myforms.rest.create', renderer='json', request_method='POST')
    config.add_route('rest_edit', '/REST/forms/edit/{id}', view='myforms.rest.edit', renderer='json', request_method='POST')
    config.add_route('rest_view', '/REST/forms/view/{id}', view='myforms.rest.view', renderer='json', request_method='GET')
    config.add_route('rest_delete', '/REST/forms/delete/{id}', view='myforms.rest.delete', renderer='json', request_method='GET')
    config.add_route('rest_error', '/REST/forms/error/{id}', view='myforms.rest.error', renderer='json', request_method='GET')
    config.add_route('rest_reports', '/REST/forms/reports/{x}/{y}', view='myforms.rest.reports', renderer='json', request_method='GET')
    config.add_route('rest_orders', '/REST/forms/orders', view='myforms.rest.orders', renderer='json', request_method='GET')
    config.add_route('rest_orders_new', '/REST/forms/new', view='myforms.rest.new', renderer='json', request_method='POST')
    config.add_route('rest_orders_paid', '/REST/forms/paid/{id}', view='myforms.rest.paid', renderer='json', request_method='GET')
    return config.make_wsgi_app()
