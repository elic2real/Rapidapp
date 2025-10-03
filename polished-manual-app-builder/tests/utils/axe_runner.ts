import axe from 'axe-core';
export async function runAxe(page: any, opts: any) {
  // Inject axe and run scan
  await page.addScriptTag({ content: axe.source });
  return await page.evaluate(async (options: any) => {
    // @ts-ignore
    return await window.axe.run(document, options);
  }, opts);
}
