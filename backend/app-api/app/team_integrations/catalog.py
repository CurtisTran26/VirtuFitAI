"""An CatalogService behavior adapted to Giap SQL schema, not a copy of its ORM.
Category UUID, price_vnd, and color/size on the SAME product_variants row.
"""
from fastapi import HTTPException
from sqlalchemy import text


def list_products(db, detail, *, q='', category_id=None, page=1, limit=20,
                  min_price=None, max_price=None, color=None, size=None,
                  in_stock_only=False, sort_by='newest'):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(422, detail={'code':'PRICE_RANGE_INVALID', 'message':'Giá tối thiểu phải nhỏ hơn hoặc bằng giá tối đa.'})
    filters = ['p.is_active', 'c.is_active', '(p.name ILIKE :q OR p.sku ILIKE :q OR p.description ILIKE :q)']
    args = {'q':'%'+q.strip()+'%', 'limit':limit, 'offset':(page-1)*limit}
    for key, expr, value in [('cat','p.category_id=:cat',category_id),('min','p.price_vnd>=:min',min_price),('max','p.price_vnd<=:max',max_price)]:
        if value is not None:
            filters.append(expr); args[key] = value
    variants = ['v.product_id=p.id']
    if color:
        variants.append('lower(v.color)=lower(:color)'); args['color'] = color.strip()
    if size:
        variants.append('lower(v.size)=lower(:size)'); args['size'] = size.strip()
    if in_stock_only:
        variants.append('v.stock_on_hand>0')
    if color or size or in_stock_only:
        filters.append('EXISTS (SELECT 1 FROM product_variants v WHERE '+' AND '.join(variants)+')')
    where = ' FROM products p JOIN categories c ON c.id=p.category_id WHERE '+' AND '.join(filters)
    total = db.execute(text('SELECT count(*)'+where), args).scalar_one()
    order = {'newest':'p.created_at DESC,p.id','price_asc':'p.price_vnd ASC,p.id','price_desc':'p.price_vnd DESC,p.id'}[sort_by]
    ids = db.execute(text('SELECT p.id'+where+' ORDER BY '+order+' LIMIT :limit OFFSET :offset'), args).scalars().all()
    return {'items':[detail(db, uid) for uid in ids], 'total':total, 'page':page, 'limit':limit,
            'page_size':limit,'total_pages':(total+limit-1)//limit}
