import CytoscapeComponent from 'react-cytoscapejs';

export const GraphVisualization = ({ elements }: { elements: any }) => {
  return (
    <div className="h-full w-full bg-slate-900 rounded-lg border border-slate-800">
       <CytoscapeComponent elements={elements} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}
