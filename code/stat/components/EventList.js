export default function EventList(props) {
  return (
    <ul className="event-list">
      {props.events.map(ev => <EventListItem key={ev.id} event={ev} />)}
    </ul>
  )
}

function EventListItem({event}) {
  return (
    <li>{event.id}: {event.text}</li>
  )
}
