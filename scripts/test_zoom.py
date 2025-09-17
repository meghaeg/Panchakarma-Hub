from zoom_service import build_iso_time_for_today, create_zoom_meeting


def main():
    start_time = build_iso_time_for_today('18:15')
    print('Creating Zoom meeting at', start_time)
    mtg = create_zoom_meeting('Panchakarma Consultation Test', start_time, 15)
    print('Created meeting:')
    for k in ('id', 'join_url', 'start_url'):
        print(f"  {k}: {mtg.get(k)}")


if __name__ == '__main__':
    main()


