export default function EventList(props) {
  return (
    <ul className="event-list">
      {props.events.map(ev => <EventListItem key={ev.id} event={ev} remove={() => props.remove(ev.id)} edit={() => props.edit(ev.id)} hover={props.hoverLang} />)}
    </ul>
  )
}

function EventListItem({event, remove, edit, hover}) {
  return (
    <li onMouseEnter={() => hover([event.id])} onMouseLeave={() => hover()}>{event.id}: {event.text} <div style={{display: 'flex'}}><button onClick={edit}>&#43;</button><button onClick={remove}>&times;</button></div></li>
  )
}
