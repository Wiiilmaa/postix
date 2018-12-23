
const priceMap = {
    "id_bills_automated-0-bill_5": 5,
    "id_bills_automated-0-bill_10": 10,
    "id_bills_automated-0-bill_20": 20,
    "id_bills_automated-0-bill_50": 50,
    "id_bills_automated-0-bill_100": 100,
    "id_bills_automated-0-bill_200": 200,
    "id_bills_automated-0-bill_500": 500,
    "id_bills_bulk-0-bill_500": 500,
    "id_bills_bulk-0-bill_1000": 1000,
    "id_bills_bulk-0-bill_2000": 2000,
    "id_bills_bulk-0-bill_5000": 5000,
    "id_bills_bulk-0-bill_10000": 10000,
    "id_bills_bulk-0-bill_20000": 20000,
    "id_bills_bulk-0-bill_50000": 50000,
    "id_bills_manually-0-bill_5": 5,
    "id_bills_manually-0-bill_10": 10,
    "id_bills_manually-0-bill_20": 20,
    "id_bills_manually-0-bill_50": 50,
    "id_bills_manually-0-bill_100": 100,
    "id_bills_manually-0-bill_200": 200,
    "id_bills_manually-0-bill_500": 500,
    "id_coins_automated-0-coin_200": 2,
    "id_coins_automated-0-coin_100": 1,
    "id_coins_automated-0-coin_50": 0.5,
    "id_coins_automated-0-coin_20": 0.2,
    "id_coins_automated-0-coin_10": 0.1,
    "id_coins_automated-0-coin_5": 0.05,
    "id_coins_automated-0-coin_2": 0.02,
    "id_coins_automated-0-coin_1": 0.01,
    "id_coins_bulk-0-coin_5000": 50,
    "id_coins_bulk-0-coin_2000": 20,
    "id_coins_bulk-0-coin_2500": 25,
    "id_coins_bulk-0-coin_800": 8,
    "id_coins_bulk-0-coin_250": 2.5,
    "id_coins_bulk-0-coin_400": 4,
    "id_coins_bulk-0-coin_100": 1,
    "id_coins_bulk-0-coin_50": 0.5,
}
let calculateTotal = function() {
    let runningTotal = 0;
    for (key in priceMap) {
	const value = document.querySelector('#' + key).value || 0;
	runningTotal += value * priceMap[key];
    }
    return runningTotal.toFixed(2)
}
document.querySelectorAll("#balance-form input").forEach(function (element) {
    element.addEventListener("input", function() {
	document.querySelector("#calculator-result").textContent = calculateTotal()

    }, false)
})
document.querySelector("#calculator-result").textContent = calculateTotal()
