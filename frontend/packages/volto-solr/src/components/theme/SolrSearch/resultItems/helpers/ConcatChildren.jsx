const ConcatChildren = ({ if1 = true, if2 = true, children }) => (
  //  if1 || if2 ? (
  <>
    {children[0]}
    {children[1]}
    {if1 && if2 ? ' | ' : null}
    {children[2]}
  </>
);
//  ) : null;

export default ConcatChildren;
