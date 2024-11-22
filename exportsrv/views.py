# -*- coding: utf-8 -*-

from flask import current_app, request, Blueprint, Response
from flask_discoverer import advertise

import json

from exportsrv.utils import get_solr_data
from exportsrv.formatter.ads import adsFormatter, adsCSLStyle, adsJournalFormat
from exportsrv.formatter.cslJson import CSLJson
from exportsrv.formatter.csl import CSL
from exportsrv.formatter.xmlFormat import XMLFormat
from exportsrv.formatter.bibTexFormat import BibTexFormat
from exportsrv.formatter.fieldedFormat import FieldedFormat
from exportsrv.formatter.customFormat import CustomFormat
from exportsrv.formatter.voTableFormat import VOTableFormat
from exportsrv.formatter.rssFormat import RSSFormat
from exportsrv.tests.unittests.stubdata import solrdata

bp = Blueprint('export_service', __name__)



def default_solr_fields(author_limit=0):
    """

    :param author_limit:
    :return: list of fields needed from solr
    """
    if author_limit == 0:
        return 'author,title,year,pubdate,pub,pub_raw,issue,volume,page,page_range,aff,aff_canonical,doi,abstract,' \
               'read_count,bibcode,identifier,copyright,keyword,doctype,[citations],comment,pubnote,version,' \
               'property,esources,data,isbn,eid,issn,arxiv_class,editor,series,publisher,bibstem,page_count,orcid_pub'
    # if the limit is specified, include it in
    return 'author,title,year,pubdate,pub,pub_raw,issue,volume,page,page_range,aff,aff_canonical,doi,abstract,' \
           'read_count,bibcode,identifier,copyright,keyword,doctype,[citations],comment,pubnote,version,' \
           'property,esources,data,isbn,eid,issn,arxiv_class,editor,series,publisher,bibstem,page_count,orcid_pub,' \
           f'[fields author={author_limit}],[fields aff={author_limit}],[fields aff_canonical={author_limit}]'


def return_response(results, status, request_type=''):
    """

    :param results: results in a dict
    :param status: status code
    :return:
    """

    if status != 200:
        current_app.logger.error('sending response status={status}'.format(status=status))
        current_app.logger.error('sending response text={response}'.format(response=results))
        r = Response(response=json.dumps(results), status=status)
        r.headers['content-type'] = 'application/json'
        return r

    if request_type == 'POST':
        current_app.logger.info('sending response status={status}'.format(status=status))
        r = Response(response=json.dumps(results), status=status)
        r.headers['content-type'] = 'application/json'
        return r

    if request_type == 'GET':
        current_app.logger.info('sending response status={status}'.format(status=status))
        r = Response(response=results['export'], status=status)
        r.headers['content-type'] = 'text/plain'
        return r

    return None


def return_bibTex_format_export(solr_data, include_abs, keyformat, max_author, author_cutoff, journal_format, request_type='POST'):
    """

    :param include_abs:
    :return:
    """
    if (solr_data is not None):
        bibTex_export = BibTexFormat(solr_data, keyformat=keyformat)
        return return_response(bibTex_export.get(include_abs=include_abs, max_author=max_author, author_cutoff=author_cutoff, journal_format=journal_format),
                               200, request_type)
    return return_response({'error': 'no result from solr'}, 404)


def return_fielded_format_export(solr_data, fielded_style, request_type='POST'):
    """

    :param solr_data:
    :param fielded_style:
    :return:
    """
    if (solr_data is not None):
        fielded_export = FieldedFormat(solr_data)
        if fielded_style == 'ADS':
            return return_response(fielded_export.get_ads_fielded(), 200, request_type)
        if fielded_style == 'EndNote':
            return return_response(fielded_export.get_endnote_fielded(), 200, request_type)
        if fielded_style == 'ProCite':
            return return_response(fielded_export.get_procite_fielded(), 200, request_type)
        if fielded_style == 'Refman':
            return return_response(fielded_export.get_refman_fielded(), 200, request_type)
        if fielded_style == 'RefWorks':
            return return_response(fielded_export.get_refworks_fielded(), 200, request_type)
        if fielded_style == 'MEDLARS':
            return return_response(fielded_export.get_medlars_fielded(), 200, request_type)

    return return_response({'error': 'no result from solr'}, 404)


def return_xml_format_export(solr_data, xml_style, request_type='POST'):
    """

    :param solr_data:
    :param xml_style:
    :param include_abs:
    :return:
    """
    if (solr_data is not None):
        xml_export = XMLFormat(solr_data)
        if xml_style == 'DublinCore':
            return return_response(xml_export.get_dublincore_xml(), 200, request_type)
        if xml_style == 'Reference':
            return return_response(xml_export.get_reference_xml(include_abs=False), 200, request_type)
        if xml_style == 'ReferenceAbs':
            return return_response(xml_export.get_reference_xml(include_abs=True), 200, request_type)
        if xml_style == 'JATS':
            return return_response(xml_export.get_jats_xml(), 200, request_type)


    return return_response({'error': 'no result from solr'}, 404)


def return_csl_format_export(solr_data, csl_style, export_format, journal_format, request_type='POST'):
    """

    :param solr_data:
    :param csl_style:
    :param export_format:
    :param request_type:
    :return:
    """
    if (solr_data is not None):
        csl_export = CSL(CSLJson(solr_data).get(), csl_style, export_format, journal_format)
        return return_response(csl_export.get(), 200, request_type)
    return return_response({'error': 'no result from solr'}, 404)


def return_votable_format_export(solr_data, request_type='POST'):
    """

    :param solr_data:
    :param request_type:
    :return:
    """
    if (solr_data is not None):
        votable_export = VOTableFormat(solr_data)
        return return_response(votable_export.get(), 200, request_type)
    return return_response({'error': 'no result from solr'}, 404)


def return_rss_format_export(solr_data, link, request_type='POST'):
    """

    :param solr_data:
    :param link:
    :param request_type:
    :return:
    """
    if (solr_data is not None):
        rss_export = RSSFormat(solr_data)
        return return_response(rss_export.get(link), 200, request_type)
    return return_response({'error': 'no result from solr'}, 404)


def get_payload(request):
    """
    
    :param request: 
    :return: 
    """
    try:
        payload = request.get_json(force=True)  # post data in json
    except:
        payload = dict(request.form)  # post data in form encoding

    if not payload:
        return {'error': 'no information received'}, 400
    if 'bibcode' not in payload:
        return {'error': 'no bibcode found in payload (parameter name is `bibcode`)'}, 400
    
    return {'payload': payload}, 200

def get_a_payload_value(payload, key):
    """

    :param payload:
    :param key:
    :return:
    """
    if type(payload[key]) is list:
        return payload[key][0]
    return payload[key]


def get_export_journal_format_from_payload(payload):
    """
    local method to read journal format parameter
        1: Use AASTeX macros (default)
        2: Use Journal Abbreviations
        3: Use Full Journal Name
    :param payload:
    :return:
    """
    if 'journalformat' in payload:
        journal_format = get_a_payload_value(payload, 'journalformat')
        if not adsJournalFormat().verify(journal_format):
            journal_format = adsJournalFormat.default
    else:
        journal_format = adsJournalFormat.default
    return journal_format


def export_post_payload_base(payload, style, format=-1):
    """

    :param payload:
    :param style:
    :param format:
    :return:
    """
    if 'sort' in payload:
        sort = get_a_payload_value(payload, 'sort')
    else:
        sort = 'date desc, bibcode desc'
    if 'authorlimit' in payload:
        author_limit = get_a_payload_value(payload, 'authorlimit')
    else:
        author_limit = 0

    bibcodes = payload['bibcode']

    # verify bibcode is a list and has at least one non empty element
    if not isinstance(bibcodes, list) or not any(bibcodes):
        return return_response({'error': 'at least one bibcode is needed in the list'}, 400)

    if format == -1:
        current_app.logger.info('received request with bibcodes={bibcodes} to export in {style} style using sort order={sort}'.
                    format(bibcodes=','.join(bibcodes), style=style, sort=sort))
    else:
        current_app.logger.info('received request with bibcodes={bibcodes} to export in {style} style with output format {format} using sort order={sort}'.
                    format(bibcodes=','.join(bibcodes), style=style, format=format, sort=sort))

    # if in the test mode, return test solr data
    if current_app.config['EXPORT_SERVICE_TEST_BIBCODE_GET'] == bibcodes:
        return solrdata.data, 200

    return get_solr_data(bibcodes=bibcodes, fields=default_solr_fields(author_limit), sort=sort, encode_style=adsFormatter().native_encoding(format)), 200


def export_post_payload_BibTex(payload, style):
    """

    :param payload:
    :param style:
    :return:
    """

    if 'maxauthor' in payload:
        max_author = get_a_payload_value(payload, 'maxauthor')
        if max_author < 0:
            max_author = 0
    elif style == 'BibTex':
        max_author = 10
    else:
        # for BibTex Abs default is to display all authors and hence 0
        max_author = 0
    if 'keyformat' in payload:
        keyformat = get_a_payload_value(payload, 'keyformat')
    else:
        keyformat = '%R'
    if 'authorcutoff' in payload:
        author_cutoff = get_a_payload_value(payload, 'authorcutoff')
        if author_cutoff <= 0:
            author_cutoff = 200
    else:
        author_cutoff = 200
    journal_format = get_export_journal_format_from_payload(payload)
    return max_author, keyformat, author_cutoff, journal_format


def get_export_format_for_journal_style(payload, style):
    """

    :param payload:
    :param style:
    :return:
    """
    # for the following 3 there is a param to specify if journal should be turn into the macro
    if style in ['aastex', 'aspc', 'aasj']:
        if payload:
            return get_export_journal_format_from_payload(payload)

    # default for the following four is to keep the full journal name, and hence 3
    if style in ['icarus', 'mnras', 'soph', 'apsj']:
        return 3
    
    return -1


def export_get(bibcode, style, format=-1):
    """

    :param bibcode:
    :param style:
    :param format:
    :return:
    """
    if format == -1:
        current_app.logger.debug('received request with bibcode={bibcode} to export in {style} style'.
                    format(bibcode=bibcode, style=style))
    else:
        current_app.logger.debug('received request with bibcode={bibcode} to export in {style} style with output format {format}'.
                    format(bibcode=bibcode, style=style, format=format))

    sort = 'date desc, bibcode desc'

    # if in the test mode, return test solr data
    if current_app.config['EXPORT_SERVICE_TEST_BIBCODE_GET'] == bibcode:
        return solrdata.data_2

    return get_solr_data(bibcodes=[bibcode], fields=default_solr_fields(), sort=sort, encode_style=adsFormatter().native_encoding(format))

@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/bibtex', methods=['POST'])
def bibTex_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        payload = results['payload']
        results, status = export_post_payload_base(payload, 'BibTex')
        if status == 200:
            max_author, keyformat, author_cutoff, journal_format = export_post_payload_BibTex(payload, 'BibTex')
            return return_bibTex_format_export(solr_data=results, include_abs=False,
                                               keyformat=keyformat, max_author=max_author, author_cutoff=author_cutoff,
                                               journal_format=journal_format)
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/bibtex/<bibcode>', methods=['GET'])
def bibTex_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_bibTex_format_export(solr_data=export_get(bibcode, 'BibTex'), include_abs=False,
                                       keyformat='%R', max_author=10, author_cutoff=200, journal_format=1, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/bibtexabs', methods=['POST'])
def bibTex_abs_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        payload = results['payload']
        results, status = export_post_payload_base(payload, 'BibTex Abs')
        if status == 200:
            max_author, keyformat, author_cutoff, journal_format = export_post_payload_BibTex(payload, 'BibTex Abs')
            return return_bibTex_format_export(solr_data=results, include_abs=True,
                                               keyformat=keyformat, max_author=max_author, author_cutoff=author_cutoff,
                                               journal_format=journal_format)
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/bibtexabs/<bibcode>', methods=['GET'])
def bibTex_abs_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_bibTex_format_export(solr_data=export_get(bibcode, 'BibTex Abs'), include_abs=True,
                                       keyformat='%R', max_author=0, author_cutoff=200, journal_format=1, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/ads', methods=['POST'])
def fielded_ads_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'ADS')
        if status == 200:
            return return_fielded_format_export(solr_data=results, fielded_style='ADS', request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/ads/<bibcode>', methods=['GET'])
def fielded_ads_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_fielded_format_export(solr_data=export_get(bibcode, 'ADS'), fielded_style='ADS', request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/endnote', methods=['POST'])
def fielded_endnote_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'EndNote')
        if status == 200:
            return return_fielded_format_export(solr_data=results, fielded_style='EndNote', request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/endnote/<bibcode>', methods=['GET'])
def fielded_endnote_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_fielded_format_export(solr_data=export_get(bibcode, 'EndNote'), fielded_style='EndNote', request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/procite', methods=['POST'])
def fielded_procite_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'ProCite')
        if status == 200:
            return return_fielded_format_export(solr_data=results, fielded_style='ProCite', request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/procite/<bibcode>', methods=['GET'])
def fielded_procite_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_fielded_format_export(solr_data=export_get(bibcode, 'ProCite'), fielded_style='ProCite', request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/ris', methods=['POST'])
def fielded_refman_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'Refman')
        if status == 200:
            return return_fielded_format_export(solr_data=results, fielded_style='Refman', request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/ris/<bibcode>', methods=['GET'])
def fielded_refman_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_fielded_format_export(solr_data=export_get(bibcode, 'Refman'), fielded_style='Refman', request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/refworks', methods=['POST'])
def fielded_refworks_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'RefWorks')
        if status == 200:
            return return_fielded_format_export(solr_data=results, fielded_style='RefWorks', request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/refworks/<bibcode>', methods=['GET'])
def fielded_refworks_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_fielded_format_export(solr_data=export_get(bibcode, 'RefWorks'), fielded_style='RefWorks', request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/medlars', methods=['POST'])
def fielded_medlars_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'MEDLARS')
        if status == 200:
            return return_fielded_format_export(solr_data=results, fielded_style='MEDLARS', request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/medlars/<bibcode>', methods=['GET'])
def fielded_medlars_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_fielded_format_export(solr_data=export_get(bibcode, 'MEDLARS'), fielded_style='MEDLARS', request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/dcxml', methods=['POST'])
def xml_dublincore_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'DublinCore')
        if status == 200:
            return return_xml_format_export(solr_data=results, xml_style='DublinCore')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/dcxml/<bibcode>', methods=['GET'])
def xml_dublincore_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_xml_format_export(solr_data=export_get(bibcode, 'DublinCore'), xml_style='DublinCore', request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/refxml', methods=['POST'])
def xml_ref_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'Reference')
        if status == 200:
            return return_xml_format_export(solr_data=results, xml_style='Reference')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/refxml/<bibcode>', methods=['GET'])
def xml_ref_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_xml_format_export(solr_data=export_get(bibcode, 'Reference'), xml_style='Reference', request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/refabsxml', methods=['POST'])
def xml_refabs_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'ReferenceAbs')
        if status == 200:
            return return_xml_format_export(solr_data=results, xml_style='ReferenceAbs')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/refabsxml/<bibcode>', methods=['GET'])
def xml_refabs_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_xml_format_export(solr_data=export_get(bibcode, 'ReferenceAbs'), xml_style='ReferenceAbs', request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/jatsxml', methods=['POST'])
def xml_jats_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'JATS')
        if status == 200:
            return return_xml_format_export(solr_data=results, xml_style='JATS')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/jatsxml/<bibcode>', methods=['GET'])
def xml_jats_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_xml_format_export(solr_data=export_get(bibcode, 'JATS'), xml_style='JATS', request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/aastex', methods=['POST'])
def csl_aastex_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        payload = results['payload']
        results, status = export_post_payload_base(payload, 'aastex', 2)
        if status == 200:
            journal_format = get_export_journal_format_from_payload(payload)
            return return_csl_format_export(solr_data=results,
                                            csl_style='aastex', export_format=adsFormatter.latex, journal_format=journal_format,
                                            request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/aastex/<bibcode>', methods=['GET'])
def csl_aastex_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'aastex', 2),
                                    csl_style='aastex', export_format=adsFormatter.latex, journal_format=adsJournalFormat.macro, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/icarus', methods=['POST'])
def csl_icarus_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'icarus', 2)
        if status == 200:
            return return_csl_format_export(solr_data=results,
                                            csl_style='icarus', export_format=adsFormatter.latex, journal_format=adsJournalFormat.full, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/icarus/<bibcode>', methods=['GET'])
def csl_icarus_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'icarus', 2),
                                    csl_style='icarus', export_format=adsFormatter.latex, journal_format=adsJournalFormat.full, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/mnras', methods=['POST'])
def csl_mnras_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'mnras', 2)
        if status == 200:
            return return_csl_format_export(solr_data=results,
                                            csl_style='mnras', export_format=adsFormatter.latex, journal_format=adsJournalFormat.full, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/mnras/<bibcode>', methods=['GET'])
def csl_mnras_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'mnras', 2),
                                    csl_style='mnras', export_format=adsFormatter.latex, journal_format=adsJournalFormat.full, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/soph', methods=['POST'])
def csl_soph_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'soph', 2)
        if status == 200:
            return return_csl_format_export(solr_data=results,
                                            csl_style='soph', export_format=adsFormatter.latex, journal_format=adsJournalFormat.full, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/soph/<bibcode>', methods=['GET'])
def csl_soph_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'soph', 2),
                                    csl_style='soph', export_format=adsFormatter.latex, journal_format=3, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/aspc', methods=['POST'])
def csl_aspc_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'aspc', 2)
        if status == 200:
            return return_csl_format_export(solr_data=results,
                                            csl_style='aspc', export_format=adsFormatter.latex, journal_format=adsJournalFormat.full, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/aspc/<bibcode>', methods=['GET'])
def csl_aspc_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'aspc', 2),
                                    csl_style='aspc', export_format=adsFormatter.latex, journal_format=3, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/aasj', methods=['POST'])
def csl_aasj_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'aasj', 2)
        if status == 200:
            return return_csl_format_export(solr_data=results,
                                            csl_style='aasj', export_format=adsFormatter.latex, journal_format=adsJournalFormat.full, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/aasj/<bibcode>', methods=['GET'])
def csl_aasj_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'aasj', 2),
                                    csl_style='aasj', export_format=adsFormatter.latex, journal_format=3, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/apsj', methods=['POST'])
def csl_apsj_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'apsj', 2)
        if status == 200:
            return return_csl_format_export(solr_data=results,
                                            csl_style='apsj', export_format=adsFormatter.unicode, journal_format=adsJournalFormat.full, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/apsj/<bibcode>', methods=['GET'])
def csl_apsj_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'apsj', 2),
                                    csl_style='apsj', export_format=adsFormatter.unicode, journal_format=adsJournalFormat.full, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/ieee', methods=['POST'])
def csl_ieee_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'ieee', 2)
        if status == 200:
            return return_csl_format_export(solr_data=results,
                                            csl_style='ieee', export_format=adsFormatter.unicode, journal_format=adsJournalFormat.full, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/ieee/<bibcode>', methods=['GET'])
def csl_ieee_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'ieee', 2),
                                    csl_style='ieee', export_format=adsFormatter.unicode, journal_format=adsJournalFormat.full, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/agu', methods=['POST'])
def csl_agu_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'agu', 2)
        if status == 200:
            return return_csl_format_export(solr_data=results,
                                            csl_style='agu', export_format=adsFormatter.unicode, journal_format=adsJournalFormat.full, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/agu/<bibcode>', methods=['GET'])
def csl_agu_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'agu', 2),
                                    csl_style='agu', export_format=adsFormatter.unicode, journal_format=adsJournalFormat.full, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/gsa', methods=['POST'])
def csl_gsa_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'gsa', 2)
        if status == 200:
            return return_csl_format_export(solr_data=results,
                                            csl_style='gsa', export_format=adsFormatter.unicode, journal_format=adsJournalFormat.full, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/gsa/<bibcode>', methods=['GET'])
def csl_gsa_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'gsa', 2),
                                    csl_style='gsa', export_format=adsFormatter.unicode, journal_format=adsJournalFormat.full, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/ams', methods=['POST'])
def csl_ams_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'ams', 2)
        if status == 200:
            return return_csl_format_export(solr_data=results,
                                            csl_style='ams', export_format=adsFormatter.unicode, journal_format=adsJournalFormat.full, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/ams/<bibcode>', methods=['GET'])
def csl_ams_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_csl_format_export(solr_data=export_get(bibcode, 'ams', 2),
                                    csl_style='ams', export_format=adsFormatter.unicode, journal_format=adsJournalFormat.full, request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/csl', methods=['POST'])
def csl_format_export():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        payload = results['payload']

        if 'style' not in payload:
            return return_response({'error': 'no style found in payload (parameter name is `style`)'}, 400)
        if 'format' not in payload:
            return return_response({'error': 'no output format found in payload (parameter name is `format`)'}, 400)

        csl_style = payload['style']
        export_format = payload['format']

        if (not adsCSLStyle().verify(csl_style)):
            return return_response({'error': 'unrecognizable style (supprted formats are: ' + adsCSLStyle().get() + ')'}, 400)
        if (not adsFormatter().verify(export_format)):
            return return_response({'error': 'unrecognizable format (supprted formats are: unicode=1, html=2, latex=3)'}, 400)

        results, status = export_post_payload_base(payload, csl_style, export_format)
        if status == 200:
            export_journal_format = get_export_format_for_journal_style(payload, csl_style)
            return return_csl_format_export(results, csl_style, export_format, export_journal_format)

    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/custom', methods=['POST'])
def custom_format_export():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        payload = results['payload']

        if 'format' not in payload:
            return return_response({'error': 'no custom format found in payload (parameter name is `format`)'}, 400)

        custom_format_str = get_a_payload_value(payload, 'format')

        if (len(custom_format_str) == 0):
            return return_response({'error': 'invalid custom format'}, 400)

        # pass the user defined format to CustomFormat to parse and we would be able to get which fields
        # in Solr we need to query on
        custom_export = CustomFormat(custom_format=custom_format_str)
        fields = custom_export.get_solr_fields()

        results, status = export_post_payload_base(payload, 'custom')
        if status == 200:
            custom_export.set_json_from_solr(results)
            return return_response(custom_export.get(), 200, 'POST')

    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/votable', methods=['POST'])
def votable_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        results, status = export_post_payload_base(results['payload'], 'VOTable')
        if status == 200:
            return return_votable_format_export(solr_data=results, request_type='POST')
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/votable/<bibcode>', methods=['GET'])
def votable_format_export_get(bibcode):
    """

    :param bibcode:
    :return:
    """
    return return_votable_format_export(solr_data=export_get(bibcode, 'VOTable'), request_type='GET')


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/rss', methods=['POST'])
def rss_format_export_post():
    """

    :return:
    """
    results, status = get_payload(request)
    if status == 200:
        payload = results['payload']
        results, status = export_post_payload_base(payload, 'RSS')
        if status == 200:
            if 'link' in payload:
                link = get_a_payload_value(payload, 'link')
            else:
                link = ''
            return return_rss_format_export(solr_data=results, link=link)
    return return_response(results, status)


@advertise(scopes=[], rate_limit=[1000, 3600 * 24])
@bp.route('/rss/<bibcode>/', defaults={'link': ''}, methods=['GET'])
@bp.route('/rss/<bibcode>/<path:link>', methods=['GET'])
def rss_format_export_get(bibcode, link):
    """

    :param bibcode:
    :param link:
    :return:
    """
    return return_rss_format_export(solr_data=export_get(bibcode, 'RSS'), link=link, request_type='GET')
