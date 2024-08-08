from routers import items, merchants, wallets, transactions, buy_item, users, authentication


def init_routers(app):
    app.include_router(users.router)
    app.include_router(authentication.router)
    app.include_router(wallets.router)
    app.include_router(merchants.router)
    app.include_router(items.router)
    app.include_router(buy_item.router)
    app.include_router(transactions.router)