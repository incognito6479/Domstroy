from drf_yasg import openapi


def get_client_params():
    status = openapi.Parameter("status", openapi.IN_QUERY, description="send imminent_payment or missed_payment",
                               type=openapi.TYPE_STRING)

    return [status, ]


def get_product_params():
    category_id = openapi.Parameter("category_id", openapi.IN_QUERY, description="send category id",
                                    type=openapi.TYPE_INTEGER)

    return [category_id, ]


def get_outcome_params():
    branch = openapi.Parameter("branch", openapi.IN_QUERY, description="send branch name", type=openapi.TYPE_STRING)
    type_id = openapi.Parameter("type_id", openapi.IN_QUERY, description="send outcome type id",
                                type=openapi.TYPE_INTEGER)
    status = openapi.Parameter("status", openapi.IN_QUERY, description="send outcome status", type=openapi.TYPE_STRING)
    whom = openapi.Parameter("whom", openapi.IN_QUERY, description="send outceome whom", type=openapi.TYPE_STRING)

    return [branch, type_id, status, whom, ]


def get_withdraw_params():
    status_ = openapi.Parameter("status", openapi.IN_QUERY, description="send status type", type=openapi.TYPE_BOOLEAN)

    return [status_, ]
