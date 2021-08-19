import { kronosLink } from './helpers';
describe('how we generated the kronos link', () => {
    it('should create a well formed url', () => {
        expect.hasAssertions();
        const jname = 'j1111-2222';
        const beams = 4;
        const utc = '2020-01-01-0:00:00';
        expect(
            kronosLink(beams, jname, utc)
        ).toBe(
            `http://astronomy.swin.edu.au/pulsar/kronos/utc_start.php?beam=${beams}&utc_start=${utc}&jname=${jname}&data=undefined`
        );
    });
});

