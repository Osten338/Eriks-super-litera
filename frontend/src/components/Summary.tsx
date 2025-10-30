type Props = {
  insertions: number
  deletions: number
  moves: number
  total: number
}

export function Summary({ insertions, deletions, moves, total }: Props) {
  return (
    <div className="text-sm text-gray-700">
      <span className="mr-3">Insertions: {insertions}</span>
      <span className="mr-3">Deletions: {deletions}</span>
      <span className="mr-3">Moves: {moves}</span>
      <span>Total: {total}</span>
    </div>
  )
}


