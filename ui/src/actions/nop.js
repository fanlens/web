/**
 * Created by chris on 14/02/2017.
 */

export const nop = () => ({type: "NOP"});

export const orNop = (cond) => (truth) => cond ? truth : nop();

export default nop;
