export const hashCode = (str) => {
  let hash = 0;
  if (str.length !== 0) {
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
  }
  return hash;
};
export const intToCol16 = (number) => {
  const pattern = "#000000";
  const base16 = Math.abs(number).toString(16);
  return pattern.substring(0, pattern.length - base16.length) + base16;
};
export const intToColHSL = (number) => {
  const abs = Math.abs(number);
  const h = abs % 360;
  const s = 75;
  const l = 60 + abs % 10;
  return `hsl(${h}, ${s}%, ${l}%)`;
};
export const strToCol = (str) => intToColHSL(hashCode(str));