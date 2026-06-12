from django.db import connection

def get_tenant_schema(request):
    """
    Returns the schema for the authenticated user's organization.
    """
    if request.user.is_authenticated:
        try:
            return request.user.organization_profile.organizacao.schema
        except Exception:
            return 'public'
    return 'public'

def get_tenant_cursor(request):
    """
    Returns a database cursor with the search_path set to the user's organization schema.
    Ensure public is always included for Django system tables.
    """
    schema = get_tenant_schema(request)
    cursor = connection.cursor()
    cursor.execute(f'SET search_path TO "{schema}", public')
    return cursor

def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict
    """
    if cursor.description is None:
        return []
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def dictfetchone(cursor):
    """
    Return one row from a cursor as a dict
    """
    if cursor.description is None:
        return None
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row:
        return dict(zip(columns, row))
    return None

def execute_paginated_query(request, base_query, params, page_number, per_page=10):
    """
    Executes a paginated query directly in the database using LIMIT and OFFSET.
    Returns (results, total_count).
    """
    offset = (int(page_number) - 1) * per_page

    # Count query
    count_query = f"SELECT COUNT(*) FROM ({base_query}) AS total"

    # Paginated query
    paginated_query = f"{base_query} LIMIT %s OFFSET %s"
    paginated_params = list(params) + [per_page, offset]

    with get_tenant_cursor(request) as cursor:
        # Get count
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        # Get data
        cursor.execute(paginated_query, paginated_params)
        results = dictfetchall(cursor)

    return results, total_count
