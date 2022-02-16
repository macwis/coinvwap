import logging
from typing import Dict, List
from collections import deque


class VWAPStore:
    def __init__(self) -> None:
        self.prices_n_vols = {
            "BTC-USD": deque(maxlen=200),
            "ETH-USD": deque(maxlen=200),
            "ETH-BTC": deque(maxlen=200),
        }

    def store(self, payload: Dict) -> None:
        if payload["type"] == "ticker":
            self._put(
                payload["product_id"],
                float(payload["price"]),
                float(payload["last_size"]),
            )

    def _put(self, product_id: str, price: float, last_size: float) -> None:
        if (
            product_id in self.prices_n_vols.keys()  # pylint: disable=consider-iterating-dictionary
        ):
            self.prices_n_vols[product_id].append((price, last_size))
        else:
            # TODO: more pro exception handling to be added
            logging.debug("Unknown product!")

    @staticmethod
    def vwap(prices: List[float], quantity: List[float]) -> float:
        if len(quantity) == 0:
            return 0.0
        return sum([pj * qj for pj, qj in zip(prices, quantity)]) / sum(quantity)

    @staticmethod
    def vwap_formated(prices: List[float], vols: List[float]):
        return f"{VWAPStore.vwap(prices, vols):010f}"

    def report(self, point_counts=False) -> str:
        buff = ""
        for product_id, product_item in self.prices_n_vols.items():
            prices = [val[0] for val in product_item]
            vols = [val[1] for val in product_item]
            buff += f"{product_id}\t{VWAPStore.vwap_formated(prices, vols)}"
            if point_counts:
                buff += "\tpoints:\t{len(prices_n_vols[product_id])}"
            buff += "\n"
        return buff
