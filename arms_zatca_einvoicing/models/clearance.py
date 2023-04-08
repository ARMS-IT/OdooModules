import requests

headers = {
    'accept': 'application/json',
    'accept-language': 'en',
    'Clearance-Status': '0',
    'Accept-Version': 'V2',
    'Authorization': 'Basic TUlJRDFEQ0NBM21nQXdJQkFnSVRid0FBZTNVQVlWVTM0SS8rNVFBQkFBQjdkVEFLQmdncWhrak9QUVFEQWpCak1SVXdFd1lLQ1pJbWlaUHlMR1FCR1JZRmJHOWpZV3d4RXpBUkJnb0praWFKay9Jc1pBRVpGZ05uYjNZeEZ6QVZCZ29Ka2lhSmsvSXNaQUVaRmdkbGVIUm5ZWHAwTVJ3d0dnWURWUVFERXhOVVUxcEZTVTVXVDBsRFJTMVRkV0pEUVMweE1CNFhEVEl5TURZeE1qRTNOREExTWxvWERUSTBNRFl4TVRFM05EQTFNbG93U1RFTE1Ba0dBMVVFQmhNQ1UwRXhEakFNQmdOVkJBb1RCV0ZuYVd4bE1SWXdGQVlEVlFRTEV3MW9ZWGxoSUhsaFoyaHRiM1Z5TVJJd0VBWURWUVFERXdreE1qY3VNQzR3TGpFd1ZqQVFCZ2NxaGtqT1BRSUJCZ1VyZ1FRQUNnTkNBQVRUQUs5bHJUVmtvOXJrcTZaWWNjOUhEUlpQNGI5UzR6QTRLbTdZWEorc25UVmhMa3pVMEhzbVNYOVVuOGpEaFJUT0hES2FmdDhDL3V1VVk5MzR2dU1ObzRJQ0p6Q0NBaU13Z1lnR0ExVWRFUVNCZ0RCK3BId3dlakViTUJrR0ExVUVCQXdTTVMxb1lYbGhmREl0TWpNMGZETXRNVEV5TVI4d0hRWUtDWkltaVpQeUxHUUJBUXdQTXpBd01EYzFOVGc0TnpBd01EQXpNUTB3Q3dZRFZRUU1EQVF4TVRBd01SRXdEd1lEVlFRYURBaGFZWFJqWVNBeE1qRVlNQllHQTFVRUR3d1BSbTl2WkNCQ2RYTnphVzVsYzNNek1CMEdBMVVkRGdRV0JCU2dtSVdENmJQZmJiS2ttVHdPSlJYdkliSDlIakFmQmdOVkhTTUVHREFXZ0JSMllJejdCcUNzWjFjMW5jK2FyS2NybVRXMUx6Qk9CZ05WSFI4RVJ6QkZNRU9nUWFBL2hqMW9kSFJ3T2k4dmRITjBZM0pzTG5waGRHTmhMbWR2ZGk1ellTOURaWEowUlc1eWIyeHNMMVJUV2tWSlRsWlBTVU5GTFZOMVlrTkJMVEV1WTNKc01JR3RCZ2dyQmdFRkJRY0JBUVNCb0RDQm5UQnVCZ2dyQmdFRkJRY3dBWVppYUhSMGNEb3ZMM1J6ZEdOeWJDNTZZWFJqWVM1bmIzWXVjMkV2UTJWeWRFVnVjbTlzYkM5VVUxcEZhVzUyYjJsalpWTkRRVEV1WlhoMFoyRjZkQzVuYjNZdWJHOWpZV3hmVkZOYVJVbE9WazlKUTBVdFUzVmlRMEV0TVNneEtTNWpjblF3S3dZSUt3WUJCUVVITUFHR0gyaDBkSEE2THk5MGMzUmpjbXd1ZW1GMFkyRXVaMjkyTG5OaEwyOWpjM0F3RGdZRFZSMFBBUUgvQkFRREFnZUFNQjBHQTFVZEpRUVdNQlFHQ0NzR0FRVUZCd01DQmdnckJnRUZCUWNEQXpBbkJna3JCZ0VFQVlJM0ZRb0VHakFZTUFvR0NDc0dBUVVGQndNQ01Bb0dDQ3NHQVFVRkJ3TURNQW9HQ0NxR1NNNDlCQU1DQTBrQU1FWUNJUUNWd0RNY3E2UE8rTWNtc0JYVXovdjFHZGhHcDdycVNhMkF4VEtTdjgzOElBSWhBT0JOREJ0OSszRFNsaWpvVmZ4enJkRGg1MjhXQzM3c21FZG9HV1ZyU3BHMQ==',
    # Already added when you pass json= but not when you pass data=
    # 'Content-Type': 'application/json',
}

json_data = {
    'invoiceHash': '79bcbc6778c268e088f737295d65f1d7',
    'uuid': '9318439a-f0fd-452e-b6f2-963e9689d93c',
    'invoice': 'PEludm9pY2UgeG1sbnM9InVybjpvYXNpczpuYW1lczpzcGVjaWZpY2F0aW9uOnVibDpzY2hlbWE6eHNkOkludm9pY2UtMiIgeG1sbnM6Y2FjPSJ1cm46b2FzaXM6bmFtZXM6c3BlY2lmaWNhdGlvbjp1Ymw6c2NoZW1hOnhzZDpDb21tb25BZ2dyZWdhdGVDb21wb25lbnRzLTIiIHhtbG5zOmNiYz0idXJuOm9hc2lzOm5hbWVzOnNwZWNpZmljYXRpb246dWJsOnNjaGVtYTp4c2Q6Q29tbW9uQmFzaWNDb21wb25lbnRzLTIiIHhtbG5zOmV4dD0idXJuOm9hc2lzOm5hbWVzOnNwZWNpZmljYXRpb246dWJsOnNjaGVtYTp4c2Q6Q29tbW9uRXh0ZW5zaW9uQ29tcG9uZW50cy0yIj4KPGNiYzpQcm9maWxlSUQ+cmVwb3J0aW5nOjEuMDwvY2JjOlByb2ZpbGVJRD4KPGNiYzpJRD4xPC9jYmM6SUQ+CjxjYmM6VVVJRD45MzE4NDM5YS1mMGZkLTQ1MmUtYjZmMi05NjNlOTY4OWQ5M2M8L2NiYzpVVUlEPgo8Y2JjOklzc3VlRGF0ZT4yMDIyLTA2LTIxPC9jYmM6SXNzdWVEYXRlPgo8Y2JjOklzc3VlVGltZT4xMzo0NzoyMzwvY2JjOklzc3VlVGltZT4KPGNiYzpJbnZvaWNlVHlwZUNvZGUgbmFtZT0iMDEwMDAwMCI+Mzg4PC9jYmM6SW52b2ljZVR5cGVDb2RlPgo8Y2JjOkRvY3VtZW50Q3VycmVuY3lDb2RlPlNBUjwvY2JjOkRvY3VtZW50Q3VycmVuY3lDb2RlPgo8Y2JjOlRheEN1cnJlbmN5Q29kZT5TQVI8L2NiYzpUYXhDdXJyZW5jeUNvZGU+CjxjYmM6TGluZUNvdW50TnVtZXJpYz4yPC9jYmM6TGluZUNvdW50TnVtZXJpYz4KPGNhYzpBZGRpdGlvbmFsRG9jdW1lbnRSZWZlcmVuY2U+CjxjYmM6SUQ+SUNWPC9jYmM6SUQ+CjxjYmM6VVVJRD4xPC9jYmM6VVVJRD4KPC9jYWM6QWRkaXRpb25hbERvY3VtZW50UmVmZXJlbmNlPgo8Y2FjOkFkZGl0aW9uYWxEb2N1bWVudFJlZmVyZW5jZT4KPGNiYzpJRD5QSUg8L2NiYzpJRD4KPGNhYzpBdHRhY2htZW50Pgo8Y2JjOkVtYmVkZGVkRG9jdW1lbnRCaW5hcnlPYmplY3QgbWltZUNvZGU9InRleHQvcGxhaW4iPk5XWmxZMlZpTmpabVptTTRObVl6T0dRNU5USTNPRFpqTm1RMk9UWmpOemxqTW1SaVl6SXpPV1JrTkdVNU1XSTBOamN5T1dRM00yRXlOMlppTlRkbE9RPT08L2NiYzpFbWJlZGRlZERvY3VtZW50QmluYXJ5T2JqZWN0Pgo8L2NhYzpBdHRhY2htZW50Pgo8L2NhYzpBZGRpdGlvbmFsRG9jdW1lbnRSZWZlcmVuY2U+CjxjYWM6QWRkaXRpb25hbERvY3VtZW50UmVmZXJlbmNlPgo8Y2JjOklEPlFSPC9jYmM6SUQ+CjxjYWM6QXR0YWNobWVudD4KPGNiYzpFbWJlZGRlZERvY3VtZW50QmluYXJ5T2JqZWN0IG1pbWVDb2RlPSJ0ZXh0L3BsYWluIj5BUmxCYkNCVFlXeGhiU0JUZFhCd2JHbGxjeUJEYnk0Z1RGUkVBZzh6TVRBeE56VXpPVGMwTURBd01ETURGREl3TWpJdE1EWXRNakZVTVRrNk1UYzZNak5hQkFjME9UYzVMak15QlFZM016a3VPREk9PC9jYmM6RW1iZWRkZWREb2N1bWVudEJpbmFyeU9iamVjdD4KPC9jYWM6QXR0YWNobWVudD4KPC9jYWM6QWRkaXRpb25hbERvY3VtZW50UmVmZXJlbmNlPgo8Y2FjOlNpZ25hdHVyZT4KPGNiYzpJRD51cm46b2FzaXM6bmFtZXM6c3BlY2lmaWNhdGlvbjp1Ymw6c2lnbmF0dXJlOkludm9pY2U8L2NiYzpJRD4KPGNiYzpTaWduYXR1cmVNZXRob2Q+dXJuOm9hc2lzOm5hbWVzOnNwZWNpZmljYXRpb246dWJsOmRzaWc6ZW52ZWxvcGVkOnhhZGVzPC9jYmM6U2lnbmF0dXJlTWV0aG9kPgo8L2NhYzpTaWduYXR1cmU+CjxjYWM6QWNjb3VudGluZ1N1cHBsaWVyUGFydHk+CjxjYWM6UGFydHk+CjxjYWM6UGFydHlJZGVudGlmaWNhdGlvbj4KPGNiYzpJRCBzY2hlbWVJRD0iTUxTIj4xMjM0NTY3ODkwPC9jYmM6SUQ+CjwvY2FjOlBhcnR5SWRlbnRpZmljYXRpb24+CjxjYWM6UG9zdGFsQWRkcmVzcz4KPGNiYzpTdHJlZXROYW1lPktpbmcgQWJkdWxheml6IFJvYWQ8L2NiYzpTdHJlZXROYW1lPgo8Y2JjOkJ1aWxkaW5nTnVtYmVyPjgyMjg8L2NiYzpCdWlsZGluZ051bWJlcj4KPGNiYzpQbG90SWRlbnRpZmljYXRpb24+MjEyMTwvY2JjOlBsb3RJZGVudGlmaWNhdGlvbj4KPGNiYzpDaXR5U3ViZGl2aXNpb25OYW1lPkFsIEFtYWw8L2NiYzpDaXR5U3ViZGl2aXNpb25OYW1lPgo8Y2JjOkNpdHlOYW1lPlJpeWFkaDwvY2JjOkNpdHlOYW1lPgo8Y2JjOlBvc3RhbFpvbmU+MTI2NDM8L2NiYzpQb3N0YWxab25lPgo8Y2JjOkNvdW50cnlTdWJlbnRpdHk+U2F1ZGkgQXJhYmlhPC9jYmM6Q291bnRyeVN1YmVudGl0eT4KPGNhYzpDb3VudHJ5Pgo8Y2JjOklkZW50aWZpY2F0aW9uQ29kZT5TQTwvY2JjOklkZW50aWZpY2F0aW9uQ29kZT4KPC9jYWM6Q291bnRyeT4KPC9jYWM6UG9zdGFsQWRkcmVzcz4KPGNhYzpQYXJ0eVRheFNjaGVtZT4KPGNiYzpDb21wYW55SUQ+MzEwMTc1Mzk3NDAwMDAzPC9jYmM6Q29tcGFueUlEPgo8Y2FjOlRheFNjaGVtZT4KPGNiYzpJRD5WQVQ8L2NiYzpJRD4KPC9jYWM6VGF4U2NoZW1lPgo8L2NhYzpQYXJ0eVRheFNjaGVtZT4KPGNhYzpQYXJ0eUxlZ2FsRW50aXR5Pgo8Y2JjOlJlZ2lzdHJhdGlvbk5hbWU+QWwgU2FsYW0gU3VwcGxpZXMgQ28uIExURDwvY2JjOlJlZ2lzdHJhdGlvbk5hbWU+CjwvY2FjOlBhcnR5TGVnYWxFbnRpdHk+CjwvY2FjOlBhcnR5Pgo8L2NhYzpBY2NvdW50aW5nU3VwcGxpZXJQYXJ0eT4KPGNhYzpBY2NvdW50aW5nQ3VzdG9tZXJQYXJ0eT4KPGNhYzpQYXJ0eT4KPGNhYzpQYXJ0eUlkZW50aWZpY2F0aW9uPgo8Y2JjOklEIHNjaGVtZUlEPSJTQUciPjEyMzQ1Nzg5MDwvY2JjOklEPgo8L2NhYzpQYXJ0eUlkZW50aWZpY2F0aW9uPgo8Y2FjOlBvc3RhbEFkZHJlc3M+CjxjYmM6U3RyZWV0TmFtZT5LaW5nIEFiZHVsbGFoIFJvYWQ8L2NiYzpTdHJlZXROYW1lPgo8Y2JjOkJ1aWxkaW5nTnVtYmVyPjM3MDk8L2NiYzpCdWlsZGluZ051bWJlcj4KPGNiYzpQbG90SWRlbnRpZmljYXRpb24+MTAwNDwvY2JjOlBsb3RJZGVudGlmaWNhdGlvbj4KPGNiYzpDaXR5U3ViZGl2aXNpb25OYW1lPlJpeWFkaCBSZWdpb248L2NiYzpDaXR5U3ViZGl2aXNpb25OYW1lPgo8Y2JjOkNpdHlOYW1lPkZyZW1vbnQ8L2NiYzpDaXR5TmFtZT4KPGNiYzpQb3N0YWxab25lPjExNTY0PC9jYmM6UG9zdGFsWm9uZT4KPGNiYzpDb3VudHJ5U3ViZW50aXR5PlNhdWRpIEFyYWJpYTwvY2JjOkNvdW50cnlTdWJlbnRpdHk+CjxjYWM6Q291bnRyeT4KPGNiYzpJZGVudGlmaWNhdGlvbkNvZGU+U0E8L2NiYzpJZGVudGlmaWNhdGlvbkNvZGU+CjwvY2FjOkNvdW50cnk+CjwvY2FjOlBvc3RhbEFkZHJlc3M+CjxjYWM6UGFydHlUYXhTY2hlbWU+CjxjYWM6VGF4U2NoZW1lPgo8Y2JjOklEPlZBVDwvY2JjOklEPgo8L2NhYzpUYXhTY2hlbWU+CjwvY2FjOlBhcnR5VGF4U2NoZW1lPgo8Y2FjOlBhcnR5TGVnYWxFbnRpdHk+CjxjYmM6UmVnaXN0cmF0aW9uTmFtZT5BTCBLQVdUSEFSIE1BUktFVFM8L2NiYzpSZWdpc3RyYXRpb25OYW1lPgo8L2NhYzpQYXJ0eUxlZ2FsRW50aXR5Pgo8L2NhYzpQYXJ0eT4KPC9jYWM6QWNjb3VudGluZ0N1c3RvbWVyUGFydHk+CjxjYWM6RGVsaXZlcnk+CjxjYmM6QWN0dWFsRGVsaXZlcnlEYXRlPjIwMjItMTAtMjc8L2NiYzpBY3R1YWxEZWxpdmVyeURhdGU+CjwvY2FjOkRlbGl2ZXJ5Pgo8Y2FjOlBheW1lbnRNZWFucz4KPGNiYzpQYXltZW50TWVhbnNDb2RlPjQyPC9jYmM6UGF5bWVudE1lYW5zQ29kZT4KPC9jYWM6UGF5bWVudE1lYW5zPgo8Y2FjOlRheFRvdGFsPgo8Y2JjOlRheEFtb3VudCBjdXJyZW5jeUlEPSJTQVIiPjYzNS45MzwvY2JjOlRheEFtb3VudD4KPGNhYzpUYXhTdWJ0b3RhbD4KPGNiYzpUYXhhYmxlQW1vdW50IGN1cnJlbmN5SUQ9IlNBUiI+NDIzOS41MDwvY2JjOlRheGFibGVBbW91bnQ+CjxjYmM6VGF4QW1vdW50IGN1cnJlbmN5SUQ9IlNBUiI+NjM1LjkzPC9jYmM6VGF4QW1vdW50Pgo8Y2FjOlRheENhdGVnb3J5Pgo8Y2JjOklEPlM8L2NiYzpJRD4KPGNiYzpQZXJjZW50PjE1PC9jYmM6UGVyY2VudD4KPGNhYzpUYXhTY2hlbWU+CjxjYmM6SUQ+VkFUPC9jYmM6SUQ+CjwvY2FjOlRheFNjaGVtZT4KPC9jYWM6VGF4Q2F0ZWdvcnk+CjwvY2FjOlRheFN1YnRvdGFsPgo8L2NhYzpUYXhUb3RhbD4KPGNhYzpUYXhUb3RhbD4KPGNiYzpUYXhBbW91bnQgY3VycmVuY3lJRD0iU0FSIj42MzUuOTM8L2NiYzpUYXhBbW91bnQ+CjwvY2FjOlRheFRvdGFsPgo8Y2FjOkxlZ2FsTW9uZXRhcnlUb3RhbD4KPGNiYzpMaW5lRXh0ZW5zaW9uQW1vdW50IGN1cnJlbmN5SUQ9IlNBUiI+NDIzOS41MDwvY2JjOkxpbmVFeHRlbnNpb25BbW91bnQ+CjxjYmM6VGF4RXhjbHVzaXZlQW1vdW50IGN1cnJlbmN5SUQ9IlNBUiI+NDIzOS41MDwvY2JjOlRheEV4Y2x1c2l2ZUFtb3VudD4KPGNiYzpUYXhJbmNsdXNpdmVBbW91bnQgY3VycmVuY3lJRD0iU0FSIj40ODc1LjQzPC9jYmM6VGF4SW5jbHVzaXZlQW1vdW50Pgo8Y2JjOkFsbG93YW5jZVRvdGFsQW1vdW50IGN1cnJlbmN5SUQ9IlNBUiI+MDwvY2JjOkFsbG93YW5jZVRvdGFsQW1vdW50Pgo8Y2JjOlBheWFibGVBbW91bnQgY3VycmVuY3lJRD0iU0FSIj40OTc5LjMyPC9jYmM6UGF5YWJsZUFtb3VudD4KPC9jYWM6TGVnYWxNb25ldGFyeVRvdGFsPgo8Y2FjOkludm9pY2VMaW5lPgo8Y2JjOklEPjE8L2NiYzpJRD4KPGNiYzpJbnZvaWNlZFF1YW50aXR5IHVuaXRDb2RlPSJQQ0UiPjEuMDA8L2NiYzpJbnZvaWNlZFF1YW50aXR5Pgo8Y2JjOkxpbmVFeHRlbnNpb25BbW91bnQgY3VycmVuY3lJRD0iU0FSIj41Ny4zOTwvY2JjOkxpbmVFeHRlbnNpb25BbW91bnQ+CjxjYWM6VGF4VG90YWw+CjxjYmM6VGF4QW1vdW50IGN1cnJlbmN5SUQ9IlNBUiI+OC42MTwvY2JjOlRheEFtb3VudD4KPGNiYzpSb3VuZGluZ0Ftb3VudCBjdXJyZW5jeUlEPSJTQVIiPjc0LjYxPC9jYmM6Um91bmRpbmdBbW91bnQ+CjwvY2FjOlRheFRvdGFsPgo8Y2FjOkl0ZW0+CjxjYmM6TmFtZT5DdXN0b21pemFibGUgRGVzayAoQ09ORklHKTwvY2JjOk5hbWU+CjxjYWM6Q2xhc3NpZmllZFRheENhdGVnb3J5Pgo8Y2JjOklEPlM8L2NiYzpJRD4KPGNiYzpQZXJjZW50PjE1PC9jYmM6UGVyY2VudD4KPGNhYzpUYXhTY2hlbWU+CjxjYmM6SUQ+VkFUPC9jYmM6SUQ+CjwvY2FjOlRheFNjaGVtZT4KPC9jYWM6Q2xhc3NpZmllZFRheENhdGVnb3J5Pgo8L2NhYzpJdGVtPgo8Y2FjOlByaWNlPgo8Y2JjOlByaWNlQW1vdW50IGN1cnJlbmN5SUQ9IlNBUiI+NzQuNjE8L2NiYzpQcmljZUFtb3VudD4KPC9jYWM6UHJpY2U+CjwvY2FjOkludm9pY2VMaW5lPgo8Y2FjOkludm9pY2VMaW5lPgo8Y2JjOklEPjU8L2NiYzpJRD4KPGNiYzpJbnZvaWNlZFF1YW50aXR5IHVuaXRDb2RlPSJQQ0UiPjEuMDA8L2NiYzpJbnZvaWNlZFF1YW50aXR5Pgo8Y2JjOkxpbmVFeHRlbnNpb25BbW91bnQgY3VycmVuY3lJRD0iU0FSIj40MTgyLjExPC9jYmM6TGluZUV4dGVuc2lvbkFtb3VudD4KPGNhYzpUYXhUb3RhbD4KPGNiYzpUYXhBbW91bnQgY3VycmVuY3lJRD0iU0FSIj42MjcuMzI8L2NiYzpUYXhBbW91bnQ+CjxjYmM6Um91bmRpbmdBbW91bnQgY3VycmVuY3lJRD0iU0FSIj41NDM2Ljc1PC9jYmM6Um91bmRpbmdBbW91bnQ+CjwvY2FjOlRheFRvdGFsPgo8Y2FjOkl0ZW0+CjxjYmM6TmFtZT5MYXJnZSBDYWJpbmV0PC9jYmM6TmFtZT4KPGNhYzpDbGFzc2lmaWVkVGF4Q2F0ZWdvcnk+CjxjYmM6SUQ+UzwvY2JjOklEPgo8Y2JjOlBlcmNlbnQ+MTU8L2NiYzpQZXJjZW50Pgo8Y2FjOlRheFNjaGVtZT4KPGNiYzpJRD5WQVQ8L2NiYzpJRD4KPC9jYWM6VGF4U2NoZW1lPgo8L2NhYzpDbGFzc2lmaWVkVGF4Q2F0ZWdvcnk+CjwvY2FjOkl0ZW0+CjxjYWM6UHJpY2U+CjxjYmM6UHJpY2VBbW91bnQgY3VycmVuY3lJRD0iU0FSIj41NDM2Ljc1PC9jYmM6UHJpY2VBbW91bnQ+CjwvY2FjOlByaWNlPgo8L2NhYzpJbnZvaWNlTGluZT4KPC9JbnZvaWNlPg==',
}

response = requests.post('https://gw-apic-gov.gazt.gov.sa/e-invoicing/developer-portal/invoices/clearance/single', headers=headers, json=json_data)
import pdb;pdb.set_trace()