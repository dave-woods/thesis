export default function ExamineString(props) {
  return (
    <div className="overlay" onClick={props.dismiss}>
      <div className="examine-string">
       <div style={{overflowX: 'auto'}}>
        <div className="source">{props.data.orig}</div>
        <div className="examined">{props.data.string.map((com, i) => <span key={i} className="component-box">{com === "" ? ' ' : com}</span>)}</div>
       </div>
       <ul className="tlinks">{props.data.tlinks.map((t, i) => <li key={i}>{t}</li>)}</ul>
      </div>
    </div>
  )
}
