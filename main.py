#!/usr/bin/env python3

import json
import locale
import pdf_report
import mail
import sys


def load_data(path):
    """Read the content of a JSON file."""
    with open(path) as json_file:
        data = json.load(json_file)
    return data


def process_data(data):
    """Processing the data, looking for maximums.
    Return a list of lines that summarize the information.
    """
    locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
    max_revenue = {"revenue": 0}
    max_sales = {"total_sales": 0}
    years_count = {}
    for item in data:
        # To convert the price from "$1234.56" to 1234.56
        item_price = locale.atof(item["price"].strip("$"))
        item["revenue"] = item["total_sales"] * item_price
        if item["revenue"] > max_revenue["revenue"]:
            max_revenue["revenue"] = item["revenue"]
            max_revenue["car"] = item["car"]

        if item["total_sales"] > max_sales["total_sales"]:
            max_sales["total_sales"] = item["total_sales"]

        if item["car"]["car_year"] in years_count:
            years_count[item["car"]["car_year"]] = {"count": years_count[item["car"]["car_year"]]["count"]+1, "total_sales": years_count[item["car"]["car_year"]]["total_sales"]+item["total_sales"]}
        else:
            years_count[item["car"]["car_year"]] = {"count": 1, "total_sales": item["total_sales"]}

    years_count = sorted(years_count.items(),key=lambda x: x[1]["count"], reverse=True)
    popular_year = years_count[0]
    summary = ["The {} generated the most revenue: ${}".format(format_car(max_revenue["car"]), max_revenue["revenue"]),
                "The {} had the most sales: {}".format(format_car(max_revenue["car"]), max_sales["total_sales"]),
                "The most popular year was {} with {} sales.".format(popular_year[0],popular_year[1]["total_sales"])]
    return summary 


def format_car(car):
    """Given a car dictionary, returns a nicely formatted name."""
    return "{} {} ({})".format(car["car_make"], car["car_model"], car["car_year"])


def cars_dict_to_table(car_data):
    """Turns 'car_data' into a list of lists."""
    table_data = [["ID", "Car", "Price", "Total Sales"]]
    for item in car_data:
        table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
    return table_data


def main(argv):
    data = load_data("sales.json")
    # summary = json.dumps(process_data(data), indent=2)
    summary = process_data(data)
    print("Sales summary for last year")
    # print('\n'.join(summary))

    # turn 'summary' into a PDF report
    table_data = cars_dict_to_table(data)
    pdf_report.generate("cars.pdf", "Sales summary", "<br/>".join(summary), table_data)

    # send the PDF report as an email attachment

    subject = "Sales summary"
    body = "\n".join(summary)
    message = mail.generate(subject, body, "cars.pdf")
    mail.send(message)
    

if __name__ == "__main__":
    main(sys.argv)