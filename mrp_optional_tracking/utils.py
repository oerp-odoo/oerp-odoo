def get_product_mrp_tracking(product):
    if product.tracking != 'none':
        return product.tracking
    return product.mrp_tracking
