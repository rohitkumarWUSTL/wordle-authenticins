import { STATUS_ALL, STATUS_IN_PROGRESS } from '../constants.js'

function StatusFilter({ value, onChange }) {
  return (
    <label className="status-filter">
      <span className="status-filter-label">Show</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value={STATUS_ALL}>All games</option>
        <option value={STATUS_IN_PROGRESS}>Active games</option>
      </select>
    </label>
  )
}

export default StatusFilter
