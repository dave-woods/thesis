export default function EventList(props) {
  return (
    <ul className="event-list">
      {props.events.map(ev => <EventListItem key={ev.id} event={ev} remove={() => props.remove(ev.id)} edit={() => props.edit(ev.id)}/>)}
    </ul>
  )
}

function EventListItem({event, remove, edit}) {
  return (
    <li>{event.id}: {event.text} <div style={{display: 'flex'}}><button onClick={edit}>&#43;</button><button onClick={remove}>&times;</button></div></li>
  )
}
