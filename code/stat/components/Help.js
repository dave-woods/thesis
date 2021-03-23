export default function Help(props) {
  return (
    <div className="help-wrap" onClick={props.dismiss}>
        <div className="help">
          <h3>TimeML Annotation</h3>
          <p>
            Use the mouse to highlight text, then press 'Tag Event' to tag that text as an event, or press 'Tag Time' to tag that text as a time.
          </p>
          <p>
            Keyboard shortcuts:
          </p>
          <ul>
            <li>E: Tag Event</li>
            <li>T: Tag Time</li>
            <li>U: Undo</li>
            <li>?: Toggle Help</li>
          </ul>
        </div>
      </div>
  )
}
