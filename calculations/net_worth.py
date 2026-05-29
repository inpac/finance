import models.investment as inv_model
import models.asset as asset_model
import models.debt as debt_model
import models.credit_card as cc_model


def total_assets(person_id: int) -> float:
    return inv_model.total_value(person_id) + asset_model.total_value(person_id)


def total_liabilities(person_id: int) -> float:
    return debt_model.total_balance(person_id) + cc_model.total_balance(person_id)


def net_worth(person_id: int) -> float:
    return total_assets(person_id) - total_liabilities(person_id)


def summary(person_id: int) -> dict:
    assets = total_assets(person_id)
    liabilities = total_liabilities(person_id)
    nw = assets - liabilities
    return {
        "total_assets": assets,
        "investments": inv_model.total_value(person_id),
        "physical_assets": asset_model.total_value(person_id),
        "total_liabilities": liabilities,
        "debts": debt_model.total_balance(person_id),
        "credit_cards": cc_model.total_balance(person_id),
        "net_worth": nw,
    }
